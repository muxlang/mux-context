# Operators: short-circuit logic and overloading

## Short-circuit logical operators

`&&` and `||` are lowered to **LLVM control flow**, not single boolean
instructions, so the right-hand side is only evaluated when needed.

A phi node selects the result based on which predecessor block executed:

```llvm
%result = phi i1 [ 0, %left_block ], [ %b_value, %right_block ]
```

- from `left_block`: constant `0` (left was false, short-circuited)
- from `right_block`: the computed right-hand value (left was true)

Lowering a single `a && b` expression instead would force both sides to evaluate
every time, remove the branch-prediction opportunity, and prevent constant
folding of the operands. The basic-block approach preserves short-circuit
semantics while letting LLVM do dead-code elimination, inlining, and
vectorization.

## Operator support and overloading

Operators are built in for primitive types and collections; they are validated
semantically and lowered to builtin operations rather than dispatched through
`Add`/`Sub`/... interfaces.

| Operator | Types |
|----------|-------|
| `+` | int, float, string, list, map, set |
| `-` `*` `/` `%` `**` | int, float |
| `==` | all types |
| `<` `>` `<=` `>=` | int, float, string, char |

For `+` on collections the semantics are type-specific: list concatenation, map
merge (latter wins on key collision), and set union. Both operands must be the
exact same collection type - no mixing and no implicit element conversions.

Code generation emits direct LLVM operations for primitives, e.g.:

```llvm
%result = add i64 %a, %b
```

Semantic validation rejects unsupported type combinations before codegen, e.g.
adding a `list` and a `set`, or `int + float` (no implicit conversions).
