# Memory model: reference counting

Mux is reference-counted: memory management is deterministic, there is no garbage
collector and no manual `free`. All objects and collections live on the heap;
primitives are passed by value, objects by reference.

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
actual `Value` ([value-representation.md](value-representation.md)).

## Operations

- **`mux_rc_inc`** - on each new reference: assigning to a new variable, passing
  as an argument, or adding to a collection.
- **`mux_rc_dec`** - when a reference leaves scope or is overwritten. When the
  count reaches zero, the memory is freed automatically (recursively for
  collections, see [collections.md](collections.md)).

## Scope-based cleanup

The compiler generates cleanup using a scope stack:

1. **Enter scope** - on function entry, if-block, loop body, match arm.
2. **Track variable** - register each reference-counted local.
3. **Exit scope** - emit decrements for all tracked variables in reverse order.

This guarantees correct cleanup order and handles early returns. The runtime
side lives in `mux-runtime/src/refcount.rs`; the codegen side in
`mux-compiler/src/codegen/memory.rs`.
