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

## Reading a document: three operations, three answers

Reading structured data conflates three things that fail differently, and Mux
gives each the wrapper its failure deserves.

| Operation | What can go wrong | Answer |
| --- | --- | --- |
| **Parse** text into a structure | Malformed input, with a position and a reason | `result` |
| **Read** a value of a given kind | It is a different kind | `result`, naming what was found |
| **Coerce** text to a type | The text does not parse as that type | `result` |

`json.parse`, `csv.parse` and `sql.connect` are the first. `Json.as_int` and
`SqlValue.as_int` are the second. A CSV cell read as an `int` is the third,
because a cell is always text.

The middle row was `optional` at first, on the reasoning that "is this an int"
has no answer beyond yes or no. That was wrong in practice: a config with
`"port": "8080"` quoted gave back `none`, and the reader could not tell a string
from a null from an absent field. The kind that WAS there is real information,
and on the SQL side it was already being computed and then discarded. So the
accessors report it:

```
expected an int, found a string
```

One deliberate exception stays an `optional`: asking whether a field is present
at all. Absence there is the question being asked rather than a failure of
expectation, and keeping it an optional is what lets an `optional<T>` field
accept a missing key while a required one reports it.

### Prefer declaring the shape

Accessors are the escape hatch. A document whose shape can be described should
be read into a class, where the error names the field as well:

```mux
class Config { int port  string host }

match Config.from_json(text) {
    ok(cfg) { ... }
    err(e)  { print(e) }   // field 'port': expected an int
}
```

`Json` exists because Mux containers are homogeneous - `{"port": 8080, "host":
"localhost"}` is a type error as a Mux map, and `[1, "two", true]` is legal JSON
that no Mux list can hold. Those are the cases the accessors remain for.
