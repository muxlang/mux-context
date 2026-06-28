# Collections and nesting

Mux's `list`, `map`, and `set` can hold any `Value`, which is what enables
arbitrary nesting (e.g. `list<map<string, list<int>>>`).

## Implementations

| Collection | Backing type | Use case |
|------------|--------------|----------|
| `list<T>` | `Vec<Value>` | contiguous, indexed access |
| `map<K,V>` | `BTreeMap<Value, Value>` | key/value pairs, sorted keys |
| `set<T>` | `BTreeSet<Value>` | unique elements, membership |

## Why BTree, not Hash

`map` and `set` use the B-tree variants rather than hash maps for:

- **Deterministic iteration order** - always the same order.
- **Ordered operations** - first/last element, range queries.
- **Reproducible output** - `to_string()` is stable, which matters for the
  golden-file snapshot tests in `mux-compiler`.

## How nesting is tracked

The type system threads nesting through all three stages
([value-representation.md](value-representation.md)):

1. **Parser** builds nested `TypeNode` structures.
2. **Semantic analyzer** resolves them to nested `Type` values.
3. **Codegen** emits the matching LLVM types.

## Reference counting in collections

Collections are reference-count-allocated and contain reference-count-allocated
values. When a collection's count reaches zero, its backing `Vec`/`BTree` is
dropped, each contained value is decremented, and nested collections are freed
recursively. See [memory.md](memory.md).
