# Collections and nesting

Mux's `list`, `map`, and `set` can hold any `Value`, which is what enables
arbitrary nesting (e.g. `list<map<string, list<int>>>`).

## Implementations

| Collection | Backing type | Use case |
|------------|--------------|----------|
| `list<T>` | `Vec<Value>` | contiguous, indexed access |
| `map<K,V>` | `OrderedMap<Value, Value>` | key/value pairs, insertion-order iteration |
| `set<T>` | `OrderedSet<Value>` | unique elements, membership |

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

## Hash tables with insertion-order iteration

`map` and `set` are backed by `OrderedMap`/`OrderedSet` in `mux-runtime`:
a `hashbrown::HashTable` of slab indices plus an intrusive doubly-linked list
through the slab. That combination is what gives both average-case O(1)
operations and insertion order, which a plain `HashMap` would not.

They replaced the B-tree variants for:

- **Average-case O(1) operations** - lookup, insertion and removal are expected
  constant time rather than the B-tree's worst-case O(log n), which is what a
  user of a hash-based collection expects from any other language. The
  guarantee is average-case, not worst-case: adversarial or degenerate hashing
  collapses a bucket to a linear scan, and insertion is amortized because the
  table resizes. A type whose `hash` is poorly distributed pays for it here.
- **Insertion-order iteration** - deterministic without being sorted, so a
  `map` prints the way it was built. Re-assigning an existing key keeps its
  original position, matching Python and JavaScript.
- **`Hashable` becomes implementable** - nothing in the runtime hashed while
  the collections were trees, so a type could not opt into being a key.

The order links cost two `usize` per entry over a B-tree node, which is the
price of iterating in insertion order. Equality and hashing stay
order-insensitive: two maps with the same pairs are equal however they were
built.

## How nesting is tracked

The type system threads nesting through all three stages
([value-representation.md](value-representation.md)):

1. **Parser** builds nested `TypeNode` structures.
2. **Semantic analyzer** resolves them to nested `Type` values.
3. **Codegen** emits the matching LLVM types.

## Reference counting in collections

Collections are reference-count-allocated and contain reference-count-allocated
values. When a collection's count reaches zero, its backing storage is
dropped, each contained value is decremented, and nested collections are freed
recursively. See [memory.md](memory.md).
