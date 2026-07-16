# Collections and nesting

Mux's `list`, `map`, and `set` can hold any `Value`, which is what enables
arbitrary nesting (e.g. `list<map<string, list<int>>>`).

## Implementations

| Collection | Backing type | Use case |
|------------|--------------|----------|
| `list<T>` | `Vec<Value>` | contiguous, indexed access |
| `map<K,V>` | `BTreeMap<Value, Value>` | key/value pairs, sorted keys |
| `set<T>` | `BTreeSet<Value>` | unique elements, membership |

## Empty literals: `{}` is a set, `{:}` is a map

`map` and `set` share brace syntax, so an empty `{}` is ambiguous on its face.
Mux resolves this in the grammar rather than the type system: **`{}` is always
the empty set, and the empty map is spelled `{:}`.**

The alternative - inferring which one `{}` meant from the surrounding expected
type - is what the compiler used to do, via a third `Type::EmptySetOrMap` that
every stage had to carry and a span-keyed override map that rewrote the type
after the fact. It worked, but the ambiguity leaked into semantics and codegen,
and an empty literal with no expected type to resolve against had no answer.
`{:}` removes the ambiguity at the source, so `EmptySetOrMap` and the override
machinery are gone (mux-compiler#266).

Consequences worth knowing:

- `{}` in a map-typed position is a compile error, not an inference. Both
  directions of the mix-up get a targeted diagnostic naming the other spelling.
- Empty literals still need an explicit type - `{:}` alone cannot infer `K`/`V`,
  the same way `[]` cannot infer its element type.
- Nesting follows the same rule per position: `map<int, set<int>> x = {1: {}}`
  is a map of sets, while `map<int, map<int, int>> y = {1: {:}}` is a map of maps.

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
