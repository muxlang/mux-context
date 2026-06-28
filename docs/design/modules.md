# Module system

Mux uses Python-style imports resolved at compile time. Module paths map directly
to file paths.

## Import resolution

```mux
import math           // math.mux in the same directory
import shapes.circle  // shapes/circle.mux
import std.math       // stdlib math module namespace (math.*)
```

- `import foo` -> `foo.mux`
- `import shapes.circle` -> `shapes/circle.mux`
- `import std.<module>` -> the standard-library module, used as `<module>.<item>`

## Name mangling

Functions from imported modules are mangled to avoid collisions when multiple
modules define the same name:

```mux
// math.mux
func fibonacci(int n) returns int { ... }
// main.mux
import math
math.fibonacci(10)   // resolves to the mangled symbol, e.g. math!fibonacci
```

## Top-level statements and module init

Top-level statements in a module become a module-initialization function that
runs before `main()`:

```mux
// config.mux
const int MAX_USERS = 100
auto initialized = false
func init() returns void { initialized = true }
```

generates a module init (conceptually `@config.init`) that the runtime calls
during startup.

## Entry function

The user entry point is `func main() returns void`. Mux allows explicit calls to
`main()` from user code; note the program entry still invokes `main()` once at
startup, so a manual call runs `main` again.

## Dependency processing

The compiler parses all imports, builds a dependency graph, processes modules in
topological order, and generates an init function per module. See
`mux-compiler/src/module_resolver.rs`.
