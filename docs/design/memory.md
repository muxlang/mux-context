# Memory model: reference counting

Mux is reference-counted: memory management is deterministic, there is no garbage
collector and no manual `free`. All objects and collections live on the heap;
primitives are boxed at the runtime boundary
([value-representation.md](value-representation.md)). Value types (primitives,
strings, collections, objects) have **value semantics** - binding or passing a
copy produces an independent value; references (`&T`) opt into sharing.

## Layout

Every heap-allocated value is prefixed with a reference-count header:

```
+------------------+-------------+
|   RefHeader      |    Value    |
| ref_count: u64   |  (payload)  |
+------------------+-------------+
    ^
    allocation pointer
```

The header uses an atomic counter for thread-safe inc/dec; the payload holds the
actual `Value`. `mux_rc_inc` / `mux_rc_dec` adjust the count, and `mux_rc_dec`
frees the allocation (recursively, see [collections.md](collections.md)) when it
reaches zero. `mux_rc_dec` is null-safe. Runtime side: `mux-runtime/src/refcount.rs`.

## Ownership conventions

The compiler follows a single rule so every allocation is released exactly once.

- **Owned (+1) values** are produced by expressions that allocate: literals,
  constructors, collection literals, function/method calls, string concatenation,
  and boxing a primitive. The producer hands the caller a fresh reference to
  release.
- **Borrowed values** are produced by loads that read an existing owner:
  identifier and parameter loads, and field/element reads. The underlying slot
  or container still owns the reference; the reader must not release it.
- **Stores retain.** A construct that keeps a value beyond the current statement
  takes its own reference: object field assignment and enum-variant construction
  `mux_rc_inc` the stored value, collections clone on insert
  ([collections.md](collections.md)), and closure captures retain what they
  close over.
- **Binding gives value semantics.** `auto x = y` transfers ownership of an
  owned temporary into the variable's slot, but *deep-clones* a borrowed
  value-type (`mux_value_deep_clone`) so the binding is an independent copy that
  cannot alias-mutate its source. Reference-typed bindings (`&T`) store the
  handle instead of copying.

## Two-tier cleanup

The compiler emits releases in two complementary places
(`mux-compiler/src/codegen/memory.rs`).

### 1. Scope-based cleanup (named variables)

An RC scope stack tracks each reference-counted local:

1. **Enter scope** - function entry, if-block, loop body, match arm.
2. **Track variable** - register each RC-typed local's storage slot.
3. **Exit / return** - load each tracked slot and decrement, in scope order.

This handles early returns and guarantees a variable's storage is released once
its binding ends. A returned value is retained before scope cleanup runs so it
survives to the caller.

### 2. Statement-scoped temporary cleanup (unbound values)

Intermediate owned values that are never bound to a variable - a string literal,
a `to_string()`/concat result, a call result used only as an argument, a
collection literal - would otherwise leak. Each such temporary is:

1. **Spilled** into a fresh, null-initialized `alloca` in the function's entry
   block (its "slot") at the point it is produced.
2. **Released** at the enclosing statement boundary by loading the slot and
   calling the null-safe `mux_rc_dec`, then nulling the slot.

Because the slot dominates the entire function, the release is well-formed from
any later block regardless of the control flow that produced the value
(short-circuit operands, ternary arms, loop bodies); on a path that never
produced the value the slot is still null and the decrement is a no-op. LLVM's
`mem2reg` promotes these slots back to SSA/phi form, so this is effectively "let
the optimizer place the dominance-correct cleanups." A pointer is tracked at most
once, so a function that returns its own argument (e.g. an in-place `sort`)
cannot double-free it. Ownership transfer (binding, returning) removes the value
from the pending set. Temporaries are isolated per function/lambda body.

## Initialization

Fields with no explicit default are zero-initialized as **boxed** values (a
`bool` field becomes a boxed `false`, not a raw `i1`), matching how
explicitly-defaulted fields and later assignments store them. Storing a raw
scalar into a pointer-sized field slot would leave its upper bytes undefined and
make a later boxed read dereference garbage - a latent bug that only surfaced
once temporaries stopped leaking and heap memory was reused.

## String ownership at the C-ABI boundary

Runtime helpers that return an owned `*mut c_char` (`*_to_string`,
`mux_string_concat`, `mux_value_get_string`) hand the caller a C string to free
with `mux_free_string`. Conversions that immediately wrap the result in a Mux
string use `mux_new_string_from_owned_cstr`, which takes ownership of the input
and frees it after copying, rather than the borrowing `mux_new_string_from_cstr`
(used for compiler-owned static string data).

## Status and limitations

Reference-counting cleanup is correct - all executable tests pass with value
semantics and no double-frees - but not yet leak-free in every case. Known gaps,
tracked for follow-up:

- Values overwritten by reassignment (`x = ...`, `x++`) are not yet reclaimed;
  the new value is stored but the previous occupant is left to leak rather than
  risk freeing a value still borrowed elsewhere.
- Temporaries inside generic-specialized bodies and a few container operations
  are not yet released under a fully precise ownership model.

These are leaks (recoverable), never use-after-frees, and are being closed
incrementally; correctness always takes priority over reclaiming a leak.
