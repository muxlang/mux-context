# Generics: compile-time monomorphization

Mux generics are resolved entirely at compile time. The compiler generates a
specialized copy of each generic function for every concrete type instantiation,
so there is no runtime cost for generics.

## Process

1. **Type inference** - determine concrete types from the call's arguments.
2. **Name generation** - build a unique identifier, e.g. `identity$int`.
3. **Type substitution** - replace type parameters with concrete types in the AST.
4. **Code generation** - emit the specialized function body.
5. **Caching** - store generated functions to avoid regenerating them.

## Example

```mux
func identity<T>(T value) returns T { return value }

auto a = identity(42)       // generates identity$int
auto b = identity("hello")  // generates identity$string
```

Conceptually the compiler substitutes types in the AST before codegen:

```
// generic
func identity<T>(T value) returns T { ... }
// after substitution for T = int
func identity$int(int value) returns int { ... }
```

## Why monomorphization

- **Zero runtime cost** - no boxing for the call, no vtables, no type checks.
- **Static dispatch** - methods resolve at compile time (see
  [object-system.md](object-system.md)).
- **Optimization** - each specialization can be fully optimized by LLVM.

The tradeoff is code size: one copy per distinct type combination.
