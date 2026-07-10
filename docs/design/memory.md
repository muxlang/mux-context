# Memory model: reference counting

Mux is reference-counted: memory management is deterministic, there is no garbage
collector and no manual `free`. All objects and collections live on the heap;
primitives are boxed at the runtime boundary
([value-representation.md](value-representation.md)). Value types (primitives,
strings, collections, objects) have **value semantics** - the act of binding or
passing a value produces an independent copy that cannot alias-mutate its source;
references (`&T`) opt into sharing.

## Layout

Every heap-allocated value is prefixed with a reference-count header:

```
+------------------+-------------+
|   RefHeader      |    Value    |
| ref_count        |  (payload)  |
+------------------+-------------+
    ^
    allocation pointer
```

The header is an atomic counter (`AtomicUsize` - `u64` on 64-bit targets) for
thread-safe inc/dec; the payload holds the actual `Value`. `mux_rc_inc` /
`mux_rc_dec` adjust the count, and `mux_rc_dec` frees the allocation (recursively,
see [collections.md](collections.md)) when it reaches zero. `mux_rc_dec` is
null-safe. Runtime side: `mux-runtime/src/refcount.rs`.

## Ownership conventions

The compiler follows a single rule so every allocation is released exactly once.

- **Owned (+1) values** are produced by expressions that allocate: literals
  (including string literals), constructors, collection literals, function/method
  calls, string concatenation, `some`/`ok`/`err`/`none` and tuple construction,
  and boxing a primitive. The producer hands the caller a fresh reference to
  release.
- **Borrowed values** are produced by loads that read an existing owner:
  identifier and parameter loads, and field/element reads. The underlying slot
  or container still owns the reference; the reader must not release it.
- **Stores retain, and reassignment releases the old occupant.** A construct that
  keeps a value beyond the current statement takes its own reference (object field
  assignment and enum-variant construction `mux_rc_inc` the stored value,
  collections clone on insert - see [collections.md](collections.md), and closure
  captures retain what they close over). Overwriting a slot (`x = ...`, `x++`, a
  loop variable, a re-declared local) first produces the new owned value, then
  decrements the previous occupant, so reassignment neither leaks nor frees a
  value still in use.
- **Binding gives value semantics.** `auto x = y` transfers ownership of an owned
  temporary into the variable's slot, but *deep-clones* a borrowed value-type
  (`mux_value_deep_clone`) so the binding is an independent copy. Reference-typed
  bindings (`&T`) store the handle instead of copying.
- **Returning retains.** A returned value is retained before the returning scope's
  cleanup runs, so it survives to the caller at `+1`.

Runtime wrappers that build a container around a value - `mux_result_ok_value`,
`mux_optional_some_value`, `mux_new_tuple`, `mux_list_push_back`, `mux_map_get`,
and friends - **clone their argument without consuming it**. Whoever passed the
intermediate in still owns it and must release it (or construct the wrapped value
directly). Getting this wrong is the classic "wrapped an owned temporary and
leaked the intermediate" bug.

## Two-tier cleanup

The compiler emits releases in two complementary places
(`mux-compiler/src/codegen/memory.rs`).

### 1. Scope-based cleanup (named variables)

An RC scope stack tracks each reference-counted local:

1. **Enter scope** - function entry, module init, if-block, loop body, match arm.
2. **Track variable** - register each RC-typed local's storage slot.
3. **Exit / return** - load each tracked slot and decrement, innermost scope
   first (the reverse of entry order).

This handles early returns and guarantees a variable's storage is released once
its binding ends.

### 2. Statement-scoped temporary cleanup (unbound values)

Intermediate owned values that are never bound to a variable - a string literal,
a `to_string()`/concat result, a call result used only as an argument, a
collection literal, a match subject - would otherwise leak. Each such temporary
is:

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
from the pending set. Temporaries are isolated per function/lambda/module-init
body.

## Closures

Closures are not RC `Value`s - they are C-`malloc`'d with their own layout and a
dedicated reference count:

```
[ refcount | fn_ptr | captures_ptr | capture_count ]
  ^header    ^--- closure struct handed to generated code ---^
```

`captures_ptr` is null for a capture-free closure; otherwise it points at an
array of `capture_count` heap cells, each holding one owned (`+1`) reference to a
captured value (codegen `mux_rc_inc`s each capture). The runtime manages this
with `mux_closure_retain` / `mux_closure_release` (`mux-runtime/src/closure.rs`),
whose refcount is atomic. On the final release the teardown walks the capture
array, drops one reference to each captured value, and frees the heap cells, the
capture array, and the closure allocation.

Codegen tracks closures in a parallel temp/scope system that mirrors the RC one
but dispatches to `mux_closure_release` instead of `mux_rc_dec`: an owned closure
is transferred into a tracked closure variable on binding, retained on return,
and never registered as an RC temporary (which would `mux_rc_dec` a non-`Value`).
A closure passed as a parameter or aliasing another variable is borrowed and left
untracked. `sync.spawn` retains the closure for the worker thread, which releases
it when its body finishes (on both normal return and panic-unwind); the atomic
header makes that cross-thread hand-off safe.

## Program-exit global teardown

Top-level (global) variables intentionally survive module initialization so a
later `main()` can read them, so they are not released by module-init scope
cleanup. Instead, `main` releases every owned global once at program exit
(after user `main()` returns). Only globals whose storage is a boxed RC pointer
are decremented; references and function/closure globals borrow their target, and
inline value-types (e.g. an enum held as a struct) are not RC pointers, so both
are excluded.

## Initialization

Fields with no explicit default are zero-initialized as **boxed** values (a
`bool` field becomes a boxed `false`, not a raw `i1`), matching how
explicitly-defaulted fields and later assignments store them. Storing a raw
scalar into a pointer-sized field slot would leave its upper bytes undefined and
make a later boxed read dereference garbage.

Enum-typed fields are the exception: an enum is stored **inline** as a struct, not
as a boxed pointer, so its default is a zeroed inline value (the first variant).
Routing an enum-field default through the class-constructor path would wrongly
allocate a heap object for the enum and leak it.

## Object copy and destruction

Each class gets a generated copy function and destructor
(`mux-compiler/src/codegen/classes.rs`). The copy bulk-`memcpy`s the class data,
then deep-clones each **boxed** field; the destructor `mux_rc_dec`s each **boxed**
field. Both skip fields whose storage is not a pointer (inline data such as an
enum struct): the bulk copy already duplicated them and they own no heap
reference, so treating their first word as a refcount pointer would corrupt
memory.

## String ownership at the C-ABI boundary

Runtime helpers that return an owned `*mut c_char` (`*_to_string`,
`mux_string_concat`, `mux_value_get_string`) hand the caller a C string to free
with `mux_free_string`; those functions only *borrow* any `*const c_char` inputs
they receive, so the caller frees both sides. Conversions that immediately wrap
the result in a Mux string use `mux_new_string_from_owned_cstr`, which takes
ownership of the input and frees it after copying, rather than the borrowing
`mux_new_string_from_cstr` (used for compiler-owned static string data). C strings
extracted for imported/runtime `string` arguments are likewise freed by the
caller once the borrowing call returns.

## Status

Reference-counting cleanup is complete and leak-free: every executable test
program runs with value semantics, no double-frees or use-after-frees, and
**zero bytes definitely or indirectly lost under Valgrind**. Correctness always
takes priority over reclaiming a leak, and the model deliberately releases old
slot occupants only when the compiler can prove the new value is independent.

The only remaining Valgrind findings come from third-party TLS/crypto crates
(`rustls`/`ring`/`ureq`) pulled in for HTTPS - benign uninitialised-buffer and
"possibly lost" reports, not leaks in Mux code - and are covered by a documented
suppression file in the compiler repo.
