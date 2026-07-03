# result and optional

`result<T, E>` and `optional<T>` share a uniform runtime representation, which is
what lets generic code and collections hold either of them interchangeably.

## Memory layout

Conceptually both are a discriminant plus a pointer to the contained value
(boxed like every other value - see
[value-representation.md](value-representation.md)):

```rust
struct result<T, E> { discriminant: i32, data: *mut T } // 0 = ok, 1 = err
struct optional<T>  { discriminant: i32, data: *mut T } // 0 = none, 1 = some
```

The identical layout is the point: a collection or generic function can store
either type without special-casing.

## Runtime behavior

- **Discriminant** selects the active variant.
- **Data pointer** points to the contained (boxed) value.

```mux
auto opt = some(42)     // discriminant = some, data = box(42)
auto res = ok("value")  // discriminant = ok,   data = box("value")
```

## Why this design

- **Single runtime representation** - collections can store either.
- **No extra enum tag** beyond the discriminant.
- **Easy propagation** - pattern matching with `match` unpacks both.
- **Interop** - `optional` and `result` can wrap the same underlying types.

`result<T, E>` requires `E` to implement the built-in `Error` interface.

`result` and `optional` are for *recoverable* conditions. Unrecoverable failures
(division by zero, out-of-bounds access, failed assertions) terminate the process
instead - see [panics.md](panics.md).
