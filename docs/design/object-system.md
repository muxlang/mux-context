# Object system and interface dispatch

## Object representation

Class instances use shared ownership with runtime type information. Conceptually:

```rust
struct ObjectData {
    ptr: *mut c_void,       // user's object data
    type_id: TypeId,        // runtime type identifier
    size: usize,            // size for deallocation
    ref_count: AtomicUsize, // reference count
}

struct ObjectRef { data: Rc<ObjectData> }
```

Each class registers with the runtime and receives a unique `TypeId`. Allocation
records the size and an optional destructor so cleanup is correct, and the
`type_id` enables runtime type checks where needed. See
`mux-runtime/src/object.rs` for the authoritative implementation.

Mux uses an explicit `.new()` to construct instances (distinguishing class
instantiation from function calls and enum-variant construction). `new` is
reserved for the compiler-generated constructor - user methods must not be named
`new`; use named factories like `from(...)` or `with_<feature>(...)`.

The generated constructor stores every field as a **boxed** value, including
fields left at their default (a `bool` field defaults to a boxed `false`, not a
raw `i1`), so reads through the uniform boxed-pointer path are always well-formed.
The exception is an **enum-typed field**, which is stored inline as a struct and
defaulted to a zeroed inline value (the first variant) rather than a boxed
pointer. Field assignment retains the stored value, and the generated copy and
destructor deep-clone / release every *boxed* field while skipping inline fields
(the bulk copy already duplicates them and they own no heap reference). Objects
are value types: binding or passing one produces an independent deep copy unless
a reference (`&T`) is used. See [memory.md](memory.md) for the full ownership and
cleanup model.

## Interface dispatch is static

Interfaces use **static dispatch** - there is no runtime vtable lookup. VTables
are generated at compile time and method calls become direct calls:

```llvm
@vtable_Circle = constant { i32, void (i8*)* } { i32 1, void (i8*)* @Circle.draw }
```

Methods are name-mangled with their class (`Circle.draw`). Benefits:

- **Zero cost** - direct calls, no pointer indirection.
- **Inlining** - LLVM can inline interface methods.
- **Better optimization** - branch prediction, no indirect jumps.

The tradeoff: interfaces cannot be added to types from other modules (no
"extension traits"). This is the deliberate cost of avoiding dynamic dispatch.
