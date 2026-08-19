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

## No propagation operator

Mux does not have a `?` operator, and is not getting one. This has been proposed
more than once (muxlang/mux-compiler#393), so the reasoning is recorded here
rather than re-argued.

A propagation operator is an **invisible early return**. `listener.accept()?`
exits the function on the error path with nothing at the end of the line saying
so, which is exactly the control flow a reader has to see to follow the
function. Mux has no exceptions for the same reason: a `return` you cannot see
is the thing the language is trying not to have. Adding one back under a
punctuation mark would undo that deliberately.

It also does not compose with the rest of the language. `?` is only meaningful
inside a function that itself returns `result`, so the same expression is legal
or not depending on its enclosing signature - a rule that has to be learned
separately and reads as arbitrary until you know it.

### What solves the nesting instead

The problem `?` is usually raised against is real: `match` puts the happy path
*inside* a block, so a function making several fallible calls indents once per
call. Go avoids this because `if err != nil { return err }` is flat.

Mux gets the flat form from **declarations without an initializer** (0.9.0):

```mux
string address
match listener.local_addr() {
    ok(value) { address = value }
    err(e) { return err(e) }
}
// continues at the same indentation
```

Four lines per call rather than one, but the early return is written down, and
the function reads top to bottom instead of drifting right. Reading `address`
before every path assigns it is a compile error, so the flatness costs no
safety.
