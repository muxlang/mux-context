# Uniform value representation

Mux uses a single unified type to represent all runtime values, which is what
lets collections and generic code handle every type uniformly.

## The Value enum

The runtime models every value as one enum (conceptual shape; see
`mux-runtime/src/lib.rs` for the authoritative definition):

```rust
pub enum Value {
    Unit,
    Bool(bool),
    Int(i64),
    Float(OrderedFloat<f64>),
    String(String),
    List(Vec<Value>),
    Map(BTreeMap<Value, Value>),
    Set(BTreeSet<Value>),
    Tuple(Box<Tuple>),
    Optional(Option<Box<Value>>),
    Result(Result<Box<Value>, Box<Value>>),
    Object(ObjectRef),
    Opaque(Box<[u8]>),
}
```

## Boxing strategy

At the runtime boundary all primitives are **boxed** into `*mut Value` pointers:

1. **Allocation** - `mux_rc_alloc(value)` allocates a reference-count header plus
   the `Value`.
2. **Storage** - pointers are stored in variables, collections, and function
   returns.
3. **Extraction** - typed accessors (`mux_value_get_int`, etc.) unwrap the value.

This enables:

- **Generic collections** - `list<T>` works uniformly for all element types.
- **Polymorphic functions** - one function body can handle any boxed type.
- **Simple FFI** - C-ABI code passes consistent `void*`/`*mut Value` pointers.

## Three type representations

The same type is represented three times across compilation. The separation lets
error reporting keep source locations while semantic analysis stays independent
of LLVM.

| Representation | Stage | Purpose |
|----------------|-------|---------|
| `TypeNode` | AST | source locations, syntax-level types |
| `Type` | semantic analysis | resolution, inference, checking |
| `BasicTypeEnum` | codegen | LLVM IR generation |

See also [memory.md](memory.md) for how boxed values are reference-counted and
[collections.md](collections.md) for how collections store them.
