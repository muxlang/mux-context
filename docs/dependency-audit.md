# Dependency audit for Mux 0.15

Audit date: 2026-10-22. Tracking issue: [mux-context#74](https://github.com/muxlang/mux-context/issues/74).

The audit covers all nine repositories in the canonical [organization manifest](https://github.com/muxlang/.github/blob/main/repositories.txt). It reviews 160 scoped direct dependency declarations in 15 manifests, plus 15 declarations added by the compiler updater branch and two newly explicit website imports. The baseline and updater total is 175; the two ownership fixes bring the complete reviewed set to 177 scoped declarations. Repeated packages in different roles or packages are separate declarations. The companion [inventory](dependency-audit-inventory.json) records exact versions, optional/default features, feature introducers, platform conditions, source excerpts and immutable source links. Lockfiles remain in their owning repositories; this report does not duplicate their transitive package lists.

## Implementation PRs

- [Compiler dependency cleanup and security patches](https://github.com/muxlang/mux-compiler/pull/475)
- [Compiler updater and packaging](https://github.com/muxlang/mux-compiler/pull/474)
- [Website dependency cleanup](https://github.com/muxlang/mux-website/pull/118)
- [Open VSX publishing dependencies](https://github.com/muxlang/mux-syntax-highlighting/pull/51)
- [Tree-sitter tooling security patch](https://github.com/muxlang/tree-sitter-mux/pull/46)

## Findings and changes

- The website retained an unused CodeMirror editor stack after moving the playground to Monaco. Remove four CodeMirror declarations, two unused rehype highlighters, an unused hashing package and the search plugin's unused fs-extra declaration. The local plugin already uses node:fs. Its generated CommonJS files require tslib, so declare tslib directly. The root configuration imports js-yaml, so declare that directly too. Keep the existing security override range and locked version.
- The website's Vitest 4.1.11 mocker has two moderate advisories. Update Vitest and its matched coverage provider to 4.1.12. Keep Docusaurus faster: future.v4 enables its compiler/bundler defaults. Keep MDX React and framework virtual-module types because framework-generated modules consume them.
- The compiler has an unused development TOML parser. No tracked Rust source calls toml, and build.rs writes configuration as strings. Removing the declaration also removes six orphan lock entries without upgrading retained packages.
- Compiler and runtime locks differ. Compiler mysql 28.0.2 introduces lru 0.16.4 and unmaintained proc-macro-error2; runtime main already resolves mysql 28.0.3 and lru 0.18.5. The candidate compiler lock now uses mysql 28.0.3 and mysql-common-derive 0.32.2. This removes both warning paths while preserving the runtime git pin.
- Runtime dependencies provide public standard-library APIs, platform support or tests. Retain them. Removing SQL, cryptography, protocol compatibility hashes, certificate roots, capability filesystem support, or optional HTTP features would change supported behavior or security boundaries.
- The hidden Open VSX publishing package and Tree-sitter quality package have separate vulnerable transitive locks. They require focused security patches, described below. No package-count target or bulk upgrade is part of this audit.

## Baseline and method

These are origin/main commits, not the developer's mutable working branches. In particular, the runtime's existing Dependabot branch and its extra local commit were left untouched. Updater additions are listed separately because they are not part of these main-branch baselines.

| Repository | Baseline commit | Declared direct dependencies |
| --- | --- | ---: |
| mux-runtime | [12ffff9308fd](https://github.com/muxlang/mux-runtime/commit/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a) | 50 |
| mux-compiler | [f958098a6d56](https://github.com/muxlang/mux-compiler/commit/f958098a6d56d1c9c7a830cb119b79ff020ff029) | 22 |
| mux-website-api | [f21cdddb18b3](https://github.com/muxlang/mux-website-api/commit/f21cdddb18b38eb9b734848ee847aa36bc200a21) | 10 |
| mux-website | [a445ad8c4c8c](https://github.com/muxlang/mux-website/commit/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187) | 66 |
| .github | [c549d6ce47d3](https://github.com/muxlang/.github/commit/c549d6ce47d32ef5b90407b0d91fccef2a850725) | 0 |
| tree-sitter-mux | [d3443282b978](https://github.com/muxlang/tree-sitter-mux/commit/d3443282b978adcced99dd2ff33d27f850d94cf0) | 3 |
| mux-syntax-highlighting | [c16ccb5face1](https://github.com/muxlang/mux-syntax-highlighting/commit/c16ccb5face1582b5fcc6803f6dcefbffa8eb151) | 9 |
| mux-examples | [34698ff5af82](https://github.com/muxlang/mux-examples/commit/34698ff5af8279a71148dd87388a74df66449ef7) | 0 |
| mux-context | [be2adc3f31e3](https://github.com/muxlang/mux-context/commit/be2adc3f31e387f30c61316167253613fdb2b71d) | 0 |

Tracked-file manifest discovery included nested and hidden package scopes. Cargo workspace roots and API pyproject.toml were read even where they declare no package dependencies. The API has five runtime requirements, five development requirements, and a hash-pinned production requirements.lock. Its pyproject configures Ruff, mypy and coverage rather than declaring another dependency set. The website local plugin is linked from the root lock; it is not an independently installed production service.

Each declaration was traced through Rust crate namespaces, JavaScript imports/requires, TypeScript types, package scripts, workflows, generated consumers and platform code. A lack of imports alone was not enough to remove a CLI, framework peer or generated dependency. Negative searches covered every tracked file in the owning package and excluded only manifest/lock declarations as use evidence. README, AGENTS.md and hook policies were reviewed before changes.

.github, mux-examples and mux-context have no Cargo/npm/Python package manifests. Organization governance and context checks use Python's standard library and shell/GitHub CLIs; examples use the Mux toolchain and public stdlib. Their workflows still install external tools and invoke pinned actions. Those operational inputs were reviewed as configuration, not misrepresented as direct application package declarations.

## Security findings and follow-ups

Scans ran on 2026-10-22. Registry results are observations at that time, not a guarantee about future advisories. Rust baseline scans used cargo audit --no-fetch against the installed RustSec snapshot with 1,226 advisory entries. Its JSON did not report a database commit/date, so this report does not claim a fresh remote RustSec fetch. Primary advisory pages were checked separately.

| Scope | Finding and introducer | Decision |
| --- | --- | --- |
| Compiler locked runtime | mux-lang -> mux-runtime -> mysql 28.0.2 -> lru 0.16.4. [RUSTSEC-2026-0253](https://rustsec.org/advisories/RUSTSEC-2026-0253.html) is an informational unsoundness warning, fixed >=0.18.2. Panic-unwinding with a panicking key destructor can leave dangling cache links. | Patched mysql to 28.0.3, resolving lru 0.18.5. No new ignore. Current cargo audit has no vulnerability or informational warning; cargo-deny passes. |
| Compiler SQL derive chain | mux-runtime -> mysql -> mysql_common -> mysql-common-derive -> proc-macro-error2 2.0.1, [RUSTSEC-2026-0173](https://rustsec.org/advisories/RUSTSEC-2026-0173.html). | Patched mysql-common-derive to 0.32.2, replacing proc-macro-error2 with manyhow and removing its exemption. Retained the public MySQL API. The required derive subtree includes darling 0.23. |
| Compiler updater branch | ZIP extraction library 2.x has license/advisory policy conflicts. | [Compiler updater PR #474](https://github.com/muxlang/mux-compiler/pull/474) upgrades to ZIP 9.0.5 with only deflate support, versions internal path dependencies and declares MIT package metadata. Validate archive compatibility and cargo-deny on that branch. This is separate from baseline unused-TOML removal. |
| Website build/dev | @docusaurus/core -> @docusaurus/glob -> micromatch -> braces; also webpack-dev-server -> chokidar/http-proxy-middleware -> braces. [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), no published fix. | Preserve the existing exact advisory exception and its recursive gate. Do not replace the whole documentation framework or widen the exception. Revisit after an upstream fix. The scan reports 19 high affected package paths, not 19 independent root defects. |
| Website tests | vitest -> @vitest/mocker, [GHSA-qxg6-89mg-rqv8](https://github.com/advisories/GHSA-qxg6-89mg-rqv8) and [GHSA-xp26-3454-mjgp](https://github.com/advisories/GHSA-xp26-3454-mjgp). | Patch Vitest and coverage-v8 together to 4.1.12. The three moderate package paths disappear. Tests are developer tooling; keep manual mock access confined. |
| Open VSX CLI | ovsx -> @vscode/vsce -> secretlint -> globby -> fast-glob -> micromatch -> braces. Also ovsx -> follow-redirects 1.16.0 and ovsx -> markdown-it <14.3.3. | Upgrade ovsx 1.2.0 to 1.3.0. Upstream removes follow-redirects and the old VSCE/Markdown/secretlint/braces chain; audit now reports zero. Existing trusted-publishing flags remain supported. Package tests/VSIX inspection passed. No registry publish was performed. |
| Tree-sitter quality tools | eslint -> minimatch -> brace-expansion 5.0.9, including [GHSA-qhr7-859c-m2p7](https://github.com/advisories/GHSA-qhr7-859c-m2p7), [GHSA-6j4f-fj2g-mc7p](https://github.com/advisories/GHSA-6j4f-fj2g-mc7p), and [GHSA-q2hr-2g5m-vwhr](https://github.com/advisories/GHSA-q2hr-2g5m-vwhr). | Updated brace-expansion 5.0.9 to 5.0.12 within existing minimatch ^5.0.8. No override, direct-major change or grammar drift. npm checks, highlighted samples and 46 corpus cases passed; audit now reports zero. |
| Runtime main | 350 locked packages scanned; no known vulnerabilities or informational warnings in the installed RustSec snapshot. | Retain public API drivers and existing policy; do not alter the developer's unrelated runtime branch. Some existing policy ignores may now be stale and need separate source review. |
| API production | pip-audit --requirement requirements.lock --disable-pip found no known vulnerabilities. | Retain Flask, CORS, limiter, Gunicorn and Redis. Preserve hash-pinned binary-only installation, sandbox/resource limits and non-root image execution. |
| Worker, indexer, retrieval tools, syntax root | Separate npm lock audits reported zero vulnerabilities. | Retain their platform/type/build/test dependencies. This result excludes hidden ovsx-cli, which is assessed separately above. |

Duplicate Rust major versions are not by themselves a removal proof. Compiler ordered-float 4 and runtime ordered-float 5 belong to independent value models; Windows bindings have target-specific API versions. Driver/transport trees may require their own versions of hashes, socket crates or TLS helpers. Keep the existing multiple-versions warning, and upgrade consumers when compatible rather than forcing shared versions across unrelated APIs.

Feature checks retained serde_json/preserve_order for insertion-order semantics; bundled SQLite and hooks for reproducible SQLite/query interruption; UUID std/rng/v4/v7/v8 for exposed constructors; mio net/os-poll for readiness; Tokio transport/runtime features for HTTP/SQL; Quinn runtime-tokio/rustls-ring for HTTP/3; Tiberius rustls/tds73/tokio and futures adapters for SQL Server. SHA-1 and MD5 support protocol/UUID compatibility, not a new password or signature policy. No features were removed without an executable proof that supported behavior survives.

## Direct dependency dispositions

The evidence links below point to baseline source lines. A remove row links the manifest when the evidence is a whole-scope negative search; its replacement is described above. Feature gates, exact specifications and secondary evidence are in the JSON inventory. Tooling listed as devDependencies can still execute operational commands (index/publish/deploy); the role reflects the owning manifest, not an assertion that deployed code can never use it.

### mux-runtime: Cargo.toml

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `ordered-float` | runtime | Hashable and comparable floating-point values; integration-test Value construction. | retain | [src/bool.rs:66](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/bool.rs#L66) |
| `hashbrown` | runtime | Insertion-ordered collection backing hash table. | retain | [src/ordered.rs:15](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/ordered.rs#L15) |
| `libc` | runtime | Platform system calls, allocation and synchronization; FFI tests. | retain | [src/closure.rs:86](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/closure.rs#L86) |
| `chrono` | runtime | Datetime parsing, formatting and arithmetic. | retain | [src/datetime.rs:3](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/datetime.rs#L3) |
| `serde_json` | runtime/optional | JSON encoding/decoding and LSP JSON transport. | retain | [src/json.rs:191](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/json.rs#L191) |
| `serde` | runtime/optional | Custom JSON deserialization and updater release metadata. | retain | [src/json.rs:7](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/json.rs#L7) |
| `indexmap` | runtime/optional | Preserve JSON object insertion order. | retain | [src/json.rs:6](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/json.rs#L6) |
| `csv` | runtime/optional | Public CSV readers and writers. | retain | [src/data.rs:44](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/data.rs#L44) |
| `ureq` | runtime/optional | Blocking HTTP client and updater HTTPS downloads. | retain | [src/net.rs:4616](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L4616) |
| `httparse` | runtime/optional | HTTP request/response header parsing. | retain | [src/net.rs:4965](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L4965) |
| `mio` | runtime/optional | OS network readiness polling. | retain | [src/poller.rs:9](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/poller.rs#L9) |
| `socket2` | runtime/optional | Socket options and transport configuration. | retain | [src/net.rs:30](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L30) |
| `regex` | runtime/optional | Public regex operations; compiler test-output normalization. | retain | [src/regex.rs:17](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/regex.rs#L17) |
| `regex-syntax` | runtime/optional | Parse regex structure for bounded-pattern policy. | retain | [src/regex.rs:207](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/regex.rs#L207) |
| `url` | runtime/optional | URL parsing and LSP file URI conversion. | retain | [src/net.rs:1038](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L1038) |
| `idna` | runtime/optional | Internationalized hostname normalization. | retain | [src/url.rs:285](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/url.rs#L285) |
| `uuid` | runtime/optional | UUID creation/parsing and SQL UUID representation. | retain | [src/sql.rs:3207](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/sql.rs#L3207) |
| `md-5` | runtime/optional | UUID version 3 compatibility. | retain | [src/uuid.rs:11](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/uuid.rs#L11) |
| `sha1` | runtime/optional | UUID version 5 and WebSocket handshake protocol. | retain | [src/net.rs:29](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L29) |
| `ring` | runtime/optional | TLS certificate fingerprint hashing. | retain | [src/net.rs:23](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L23) |
| `sha2` | runtime/optional | SHA-2 digests, SQL authentication and updater archive integrity. | retain | [src/crypto.rs:15](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L15) |
| `sha3` | runtime/optional | Public SHA-3 digest functions. | retain | [src/crypto.rs:99](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L99) |
| `blake3` | runtime/optional | Public BLAKE3 digest functions. | retain | [src/crypto.rs:115](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L115) |
| `hmac` | runtime/optional | Public keyed HMAC operations. | retain | [src/crypto.rs:14](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L14) |
| `aes-gcm` | runtime/optional | Public authenticated AES encryption. | retain | [src/crypto.rs:12](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L12) |
| `chacha20poly1305` | runtime/optional | Public authenticated ChaCha encryption. | retain | [src/crypto.rs:217](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L217) |
| `getrandom` | runtime | OS entropy for random/crypto/network identifiers. | retain | [src/crypto.rs:160](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L160) |
| `base64` | runtime/optional | Network and crypto binary/text encoding. | retain | [src/crypto.rs:13](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L13) |
| `h2` | runtime/optional | HTTP/2 framing and streams. | retain | [src/net.rs:7799](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L7799) |
| `tokio` | runtime/optional | HTTP and SQL asynchronous transport execution. | retain | [src/net.rs:55](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L55) |
| `tokio-util` | runtime/optional | Adapt Tokio SQL streams to futures I/O. | retain | [src/sql.rs:36](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/sql.rs#L36) |
| `bytes` | runtime/optional | HTTP/2 and HTTP/3 byte buffers. | retain | [src/net.rs:18](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L18) |
| `cap-std` | runtime/optional | Directory capability boundary for network static-file serving. | retain | [src/net.rs:19](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L19) |
| `http` | runtime/optional | Typed HTTP request/response structures. | retain | [src/net.rs:222](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L222) |
| `h3` | runtime/optional | HTTP/3 framing and QPACK. | retain | [src/net.rs:485](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L485) |
| `h3-quinn` | runtime/optional | Bridge HTTP/3 to Quinn QUIC. | retain | [src/net.rs:484](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L484) |
| `quinn` | runtime/optional | QUIC transport for public HTTP/3 APIs. | retain | [src/net.rs:457](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L457) |
| `rusqlite` | runtime/optional | SQLite driver; bundled SQLite and query interruption hooks. | retain | [src/sql.rs:17](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/sql.rs#L17) |
| `postgres` | runtime/optional | PostgreSQL SQL backend. | retain | [src/sql.rs:15](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/sql.rs#L15) |
| `mysql` | runtime/optional | MySQL SQL backend. | retain | [src/sql.rs:10](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/sql.rs#L10) |
| `tiberius` | runtime/optional | SQL Server backend. | retain | [src/sql.rs:31](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/sql.rs#L31) |
| `futures-util` | runtime/optional | SQL stream adapters and result collection. | retain | [src/sql.rs:9](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/sql.rs#L9) |
| `rustls` | runtime/optional | TLS transport and certificate validation. | retain | [src/net.rs:26](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L26) |
| `webpki-roots` | runtime/optional | Public trust roots for TLS verification. | retain | [src/net.rs:1086](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L1086) |
| `chrono-tz` | runtime/optional | Named IANA time-zone support. | retain | [src/datetime_types.rs:21](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/datetime_types.rs#L21) |
| `ordered-float` | dev | Hashable and comparable floating-point values; integration-test Value construction. | retain | [tests/extern_extras_unit.rs:12](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/tests/extern_extras_unit.rs#L12) |
| `libc` | dev | Platform system calls, allocation and synchronization; FFI tests. | retain | [tests/closure_unit.rs:29](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/tests/closure_unit.rs#L29) |
| `criterion` | dev | Manual performance benchmarks, including HTML reports. | retain | [benches/hot_paths.rs:41](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/benches/hot_paths.rs#L41) |
| `windows-sys` | runtime; cfg(windows) | Windows file replacement, console or synchronization APIs. | retain | [src/crypto.rs:500](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/crypto.rs#L500) |
| `named_pipe` | runtime; cfg(windows) | Windows named-pipe IPC transport. | retain | [src/net.rs:22](https://github.com/muxlang/mux-runtime/blob/12ffff9308fd20df0e9c0c0161f61fa58ed4ba5a/src/net.rs#L22) |

### mux-compiler: mux-compiler/Cargo.toml

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `anstream` | runtime | Terminal-aware diagnostic output. | retain | [mux-compiler/src/diagnostic/emitter.rs:7](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/diagnostic/emitter.rs#L7) |
| `anstyle` | runtime | Diagnostic ANSI styles. | retain | [mux-compiler/src/diagnostic/styles.rs:7](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/diagnostic/styles.rs#L7) |
| `crossbeam-channel` | runtime | LSP event and timeout channels. | retain | [mux-compiler/src/lsp.rs:263](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/lsp.rs#L263) |
| `ordered-float` | runtime | Hashable and comparable floating-point values; integration-test Value construction. | retain | [mux-compiler/src/ast/literals.rs:2](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/ast/literals.rs#L2) |
| `unicode-width` | runtime | Diagnostic source-column display widths. | retain | [mux-compiler/src/diagnostic/emitter.rs:9](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/diagnostic/emitter.rs#L9) |
| `fs2` | runtime | Advisory locks for safe file/update replacement. | retain | [mux-compiler/src/diagnostic/fix.rs:5](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/diagnostic/fix.rs#L5) |
| `lazy_static` | runtime | Shared standard-library metadata initialization. | retain | [mux-compiler/src/semantics/stdlib.rs:30](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/semantics/stdlib.rs#L30) |
| `inkwell` | runtime | LLVM22 compiler backend. | retain | [mux-compiler/benches/compile.rs:27](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/benches/compile.rs#L27) |
| `clap` | runtime | Derive CLI argument parsers. | retain | [mux-compiler/src/main.rs:12](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/main.rs#L12) |
| `lsp-server` | runtime | Language server stdio transport. | retain | [mux-compiler/src/lsp.rs:9](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/lsp.rs#L9) |
| `lsp-types` | runtime | Language server protocol types. | retain | [mux-compiler/src/lsp.rs:10](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/lsp.rs#L10) |
| `url` | runtime | URL parsing and LSP file URI conversion. | retain | [mux-compiler/src/lsp.rs:11](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/lsp.rs#L11) |
| `mux-runtime` | runtime | ABI-coupled runtime for generated executables. | retain | [mux-compiler/src/codegen/runtime.rs:18](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/codegen/runtime.rs#L18) |
| `phf` | runtime | Compile-time standard-library name lookup tables. | retain | [mux-compiler/src/semantics/stdlib.rs:31](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/semantics/stdlib.rs#L31) |
| `serde_json` | runtime | JSON encoding/decoding and LSP JSON transport. | retain | [mux-compiler/src/format_config.rs:5](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/format_config.rs#L5) |
| `insta` | dev | Compiler regression snapshots. | retain | [mux-compiler/tests/executable_integration.rs:1](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/tests/executable_integration.rs#L1) |
| `ordered-float` | dev | Hashable and comparable floating-point values; integration-test Value construction. | retain | [mux-compiler/tests/ast_unit.rs:14](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/tests/ast_unit.rs#L14) |
| `regex` | dev | Public regex operations; compiler test-output normalization. | retain | [mux-compiler/tests/executable_integration.rs:2](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/tests/executable_integration.rs#L2) |
| `toml` | dev | No TOML parser calls remain; config generation uses strings. | remove | [mux-compiler/build.rs:143](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/build.rs#L143) |
| `criterion` | dev | Manual performance benchmarks, including HTML reports. | retain | [mux-compiler/benches/compile.rs:26](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/benches/compile.rs#L26) |
| `set-git-hooks-dir` | build | Install repository-local Git hooks from build.rs. | retain | [mux-compiler/build.rs:23](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/build.rs#L23) |
| `windows-sys` | runtime; cfg(windows) | Windows file replacement, console or synchronization APIs. | retain | [mux-compiler/src/diagnostic/fix.rs:627](https://github.com/muxlang/mux-compiler/blob/f958098a6d56d1c9c7a830cb119b79ff020ff029/mux-compiler/src/diagnostic/fix.rs#L627) |

### mux-website-api: requirements-dev.txt

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `pytest` | dev | Python regression tests. | retain | [tests/test_server.py:12](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/tests/test_server.py#L12) |
| `pytest-cov` | dev | CI server branch/line coverage gate. | retain | [.github/workflows/ci.yml:65](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/.github/workflows/ci.yml#L65) |
| `ruff` | dev | Python lint and format checks. | retain | [pyproject.toml:1](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/pyproject.toml#L1) |
| `mypy` | dev | Python static type checks. | retain | [pyproject.toml:12](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/pyproject.toml#L12) |
| `pip-audit` | dev | CI locked Python vulnerability audit. | retain | [.github/workflows/ci.yml:63](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/.github/workflows/ci.yml#L63) |

### mux-website-api: requirements.txt

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `flask` | runtime | API routing, JSON responses and request limits. | retain | [server.py:15](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/server.py#L15) |
| `flask-cors` | runtime | Explicit browser CORS boundary. | retain | [server.py:16](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/server.py#L16) |
| `flask-limiter` | runtime | Request rate limits using configured storage. | retain | [server.py:17](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/server.py#L17) |
| `gunicorn` | runtime | Production WSGI process server. | retain | [.github/workflows/ci.yml:53](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/.github/workflows/ci.yml#L53) |
| `redis` | runtime | flask-limiter production shared Redis storage driver. | retain | [server.py:48](https://github.com/muxlang/mux-website-api/blob/f21cdddb18b38eb9b734848ee847aa36bc200a21/server.py#L48) |

### mux-website: package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `@codemirror/basic-setup` | runtime | Unused former CodeMirror playground editor. | remove | [package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L1) |
| `@codemirror/lang-python` | runtime | Unused former CodeMirror playground editor. | remove | [package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L1) |
| `@codemirror/theme-one-dark` | runtime | Unused former CodeMirror playground editor. | remove | [package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L1) |
| `@docusaurus/core` | runtime | Site build, routing and generated runtime. | retain | [scripts/ci/npm-audit-gate.test.mjs:17](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/scripts/ci/npm-audit-gate.test.mjs#L17) |
| `@docusaurus/faster` | runtime | Docusaurus v4 default accelerated compiler/bundler integration. | retain | [docusaurus.config.ts:77](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/docusaurus.config.ts#L77) |
| `@docusaurus/preset-classic` | runtime | Docs/blog/theme preset configured by classic shorthand. | retain | [docusaurus.config.ts:3](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/docusaurus.config.ts#L3) |
| `@mdx-js/react` | runtime | Framework-generated MDX provider runtime peer. | retain | [docusaurus.config.ts:98](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/docusaurus.config.ts#L98) |
| `@monaco-editor/react` | runtime | React wrapper for playground Monaco editor. | retain | [src/components/MonacoEditor/index.tsx:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/src/components/MonacoEditor/index.tsx#L2) |
| `@muxlang/docusaurus-search-local` | runtime | Configured local offline-search theme. | retain | [docusaurus.config.ts:129](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/docusaurus.config.ts#L129) |
| `@shikijs/langs` | runtime | Explicit shell and JavaScript language grammars. | retain | [src/shiki/highlighter.ts:3](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/src/shiki/highlighter.ts#L3) |
| `@shikijs/rehype` | runtime | Unused former rehype syntax-highlighting pipeline. | remove | [package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L1) |
| `@uiw/react-codemirror` | runtime | Unused former CodeMirror playground editor. | remove | [package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L1) |
| `clsx` | runtime | Conditional CSS class names. | retain | [src/pages/index.tsx:3](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/src/pages/index.tsx#L3) |
| `monaco-editor` | runtime | Playground language API and editor workers. | retain | [src/monaco/muxTheme.ts:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/src/monaco/muxTheme.ts#L1) |
| `prism-react-renderer` | runtime | Docusaurus code blocks and Prism themes. | retain | [docusaurus.config.ts:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/docusaurus.config.ts#L1) |
| `react` | runtime | Site/editor UI component runtime or plugin host peer. | retain | [test/setup.ts:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/test/setup.ts#L2) |
| `react-dom` | runtime | React renderer host peer and SSR tests. | retain | [src/hooks/useModifierKeyLabel.test.ts:4](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/src/hooks/useModifierKeyLabel.test.ts#L4) |
| `react-markdown` | runtime | Render chat answers and changelog Markdown. | retain | [src/pages/changelog.tsx:4](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/src/pages/changelog.tsx#L4) |
| `rehype-highlight` | runtime | Unused prior Markdown highlighter. | remove | [package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L1) |
| `shiki` | runtime | Direct syntax highlighter and custom Mux grammar. | retain | [src/shiki/highlighter.ts:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/src/shiki/highlighter.ts#L1) |
| `@docusaurus/module-type-aliases` | devDependencies | Generated Docusaurus/theme virtual-module type declarations. | retain | [tsconfig.json:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tsconfig.json#L2) |
| `@docusaurus/tsconfig` | devDependencies | Framework TypeScript base configuration. | retain | [tsconfig.json:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tsconfig.json#L2) |
| `@docusaurus/types` | devDependencies | Site configuration types. | retain | [docusaurus.config.ts:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/docusaurus.config.ts#L2) |
| `@docusaurus/utils` | devDependencies | Search plugin server URL and build utilities. | retain | [plugins/mux-search-local/lib/server/index.js:7](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/index.js#L7) |
| `@docusaurus/utils-validation` | devDependencies | Search plugin option schema validation. | retain | [plugins/mux-search-local/lib/server/options.js:5](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/options.js#L5) |
| `@noble/hashes` | devDependencies | Unused former hashing helper. | remove | [package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L1) |
| `@testing-library/jest-dom` | devDependencies | DOM assertion extensions. | retain | [test/setup.ts:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/test/setup.ts#L1) |
| `@testing-library/react` | devDependencies | Browser component/hook tests. | retain | [test/setup.ts:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/test/setup.ts#L2) |
| `@types/js-yaml` | devDependencies | Type declarations for front matter parser. | retain | [docusaurus.config.ts:4](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/docusaurus.config.ts#L4) |
| `@vitejs/plugin-react` | devDependencies | Vitest JSX and React transforms. | retain | [vitest.config.mts:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/vitest.config.mts#L2) |
| `@vitest/coverage-v8` | devDependencies | Vitest dynamically selected coverage provider. | upgrade | [package.json:12](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L12) |
| `eslint` | devDependencies | JavaScript/TypeScript lint CLI. | retain | [eslint.config.mjs:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/eslint.config.mjs#L1) |
| `eslint-plugin-react-hooks` | devDependencies | React hooks lint rules. | retain | [eslint.config.mjs:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/eslint.config.mjs#L2) |
| `jsdom` | devDependencies | Configured Vitest browser DOM environment. | retain | [vitest.config.mts:34](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/vitest.config.mts#L34) |
| `prettier` | devDependencies | Repository formatting CLI and check script. | retain | [scripts/check-format.mjs:37](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/scripts/check-format.mjs#L37) |
| `typescript` | devDependencies | Provides the tsc executable used by the website typecheck script. | retain | [package.json:19](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/package.json#L19) |
| `typescript-eslint` | devDependencies | Typed ESLint configuration and rules. | retain | [eslint.config.mjs:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/eslint.config.mjs#L1) |
| `vitest` | devDependencies | Site/search unit and browser tests. | upgrade | [test/setup.ts:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/test/setup.ts#L1) |

### mux-website: plugins/mux-search-local/package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `@braintree/sanitize-url` | runtime | Sanitize search-result external URLs. | retain | [plugins/mux-search-local/lib/client/utils/getExternalURI.js:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/client/utils/getExternalURI.js#L1) |
| `cheerio` | runtime | Parse generated HTML for local search indexing. | retain | [plugins/mux-search-local/lib/server/utils/parse.js:5](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/utils/parse.js#L5) |
| `clsx` | runtime | Conditional CSS class names. | retain | [plugins/mux-search-local/lib/client/theme/LoadingRing/LoadingRing.jsx:3](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/client/theme/LoadingRing/LoadingRing.jsx#L3) |
| `debug` | runtime | Search index build diagnostics. | retain | [plugins/mux-search-local/lib/server/utils/debug.js:5](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/utils/debug.js#L5) |
| `fs-extra` | runtime | Unused legacy filesystem helper; source uses node:fs. | remove | [plugins/mux-search-local/package.json:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/package.json#L1) |
| `klaw-sync` | runtime | Traverse generated docs when hashing search index. | retain | [plugins/mux-search-local/lib/server/utils/getIndexHash.js:8](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/utils/getIndexHash.js#L8) |
| `lunr` | runtime | Build/query local search indexes. | retain | [plugins/mux-search-local/lib/server/utils/buildIndex.js:5](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/utils/buildIndex.js#L5) |
| `mark.js` | runtime | Highlight matched search terms in rendered pages. | retain | [plugins/mux-search-local/lib/client/theme/SearchBar/SearchBar.jsx:8](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/client/theme/SearchBar/SearchBar.jsx#L8) |
| `validate-peer-dependencies` | runtime | Validate the plugin Docusaurus/React host contract. | retain | [plugins/mux-search-local/lib/server/index.js:8](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/index.js#L8) |
| `@docusaurus/core` | peer | Site build, routing and generated runtime. | retain | [plugins/mux-search-local/lib/server/index.js:13](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/index.js#L13) |
| `@docusaurus/utils` | peer | Search plugin server URL and build utilities. | retain | [plugins/mux-search-local/lib/server/index.js:7](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/index.js#L7) |
| `@docusaurus/utils-validation` | peer | Search plugin option schema validation. | retain | [plugins/mux-search-local/lib/server/options.js:5](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/options.js#L5) |
| `react` | peer | Site/editor UI component runtime or plugin host peer. | retain | [plugins/mux-search-local/lib/client/theme/ErrorBoundary.jsx:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/client/theme/ErrorBoundary.jsx#L1) |
| `react-dom` | peer | React renderer host peer and SSR tests. | retain | [plugins/mux-search-local/lib/server/index.js:13](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/plugins/mux-search-local/lib/server/index.js#L13) |

### mux-website: tools/docs-indexer/package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `@types/js-yaml` | devDependencies | Type declarations for front matter parser. | retain | [tools/docs-indexer/src/extract.ts:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/docs-indexer/src/extract.ts#L2) |
| `@types/node` | devDependencies | Node builtin types for tooling and Worker tests. | retain | [tools/docs-indexer/src/crawl.ts:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/docs-indexer/src/crawl.ts#L1) |
| `dotenv` | devDependencies | Indexer loads local configuration via dotenv/config. | retain | [tools/docs-indexer/src/index.ts:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/docs-indexer/src/index.ts#L2) |
| `js-yaml` | devDependencies | Indexer or site front matter parsing. | retain | [tools/docs-indexer/src/extract.ts:2](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/docs-indexer/src/extract.ts#L2) |
| `tsx` | devDependencies | Execute TypeScript tooling and node:test suites. | retain | [tools/docs-indexer/package.json:6](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/docs-indexer/package.json#L6) |
| `typescript` | devDependencies | tsc typecheck CLI and shared compiler types. | retain | [tools/docs-indexer/package.json:10](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/docs-indexer/package.json#L10) |

### mux-website: tools/retrieval-test/package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `@types/node` | devDependencies | Node builtin types for tooling and Worker tests. | retain | [tools/retrieval-test/src/error-eval.ts:16](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/retrieval-test/src/error-eval.ts#L16) |
| `tsx` | devDependencies | Execute TypeScript tooling and node:test suites. | retain | [tools/retrieval-test/package.json:6](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/retrieval-test/package.json#L6) |
| `typescript` | devDependencies | tsc typecheck CLI and shared compiler types. | retain | [tools/retrieval-test/package.json:8](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/tools/retrieval-test/package.json#L8) |

### mux-website: workers/mux-ai/package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `@cloudflare/workers-types` | devDependencies | Cloudflare platform API types. | retain | [workers/mux-ai/tsconfig.json:7](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/workers/mux-ai/tsconfig.json#L7) |
| `@types/node` | devDependencies | Node builtin types for tooling and Worker tests. | retain | [workers/mux-ai/src/index.test.ts:1](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/workers/mux-ai/src/index.test.ts#L1) |
| `tsx` | devDependencies | Execute TypeScript tooling and node:test suites. | retain | [workers/mux-ai/package.json:9](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/workers/mux-ai/package.json#L9) |
| `typescript` | devDependencies | tsc typecheck CLI and shared compiler types. | retain | [workers/mux-ai/package.json:10](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/workers/mux-ai/package.json#L10) |
| `wrangler` | devDependencies | Worker local development and deployment CLI. | retain | [workers/mux-ai/src/index.ts:13](https://github.com/muxlang/mux-website/blob/a445ad8c4c8c778c9c1fa25b42ebe7cf5df18187/workers/mux-ai/src/index.ts#L13) |

### tree-sitter-mux: package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `@eslint/js` | devDependencies | ESLint recommended JavaScript rules. | retain | [eslint.config.js:1](https://github.com/muxlang/tree-sitter-mux/blob/d3443282b978adcced99dd2ff33d27f850d94cf0/eslint.config.js#L1) |
| `eslint` | devDependencies | JavaScript/TypeScript lint CLI. | retain | [eslint.config.js:1](https://github.com/muxlang/tree-sitter-mux/blob/d3443282b978adcced99dd2ff33d27f850d94cf0/eslint.config.js#L1) |
| `prettier` | devDependencies | Repository formatting CLI and check script. | retain | [package.json:8](https://github.com/muxlang/tree-sitter-mux/blob/d3443282b978adcced99dd2ff33d27f850d94cf0/package.json#L8) |

### mux-syntax-highlighting: .github/ovsx-cli/package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `ovsx` | runtime | Open VSX publish CLI in isolated release workflow. | upgrade | [.github/workflows/publish-vscode.yml:93](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/.github/workflows/publish-vscode.yml#L93) |

### mux-syntax-highlighting: package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `@eslint/js` | devDependencies | ESLint recommended JavaScript rules. | retain | [eslint.config.js:1](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/eslint.config.js#L1) |
| `@vscode/vsce` | devDependencies | Package and verify VSIX without bundling unused node_modules. | retain | [scripts/package-vscode.js:12](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/scripts/package-vscode.js#L12) |
| `c8` | devDependencies | VSCode client test coverage instrumentation. | retain | [package.json:14](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/package.json#L14) |
| `esbuild` | devDependencies | Bundle extension and language client into VSIX. | retain | [scripts/package-vscode.js:13](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/scripts/package-vscode.js#L13) |
| `eslint` | devDependencies | JavaScript/TypeScript lint CLI. | retain | [eslint.config.js:1](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/eslint.config.js#L1) |
| `prettier` | devDependencies | Repository formatting CLI and check script. | retain | [package.json:8](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/package.json#L8) |
| `yauzl` | devDependencies | Inspect packaged VSIX ZIP contents. | retain | [scripts/verify-vsix.js:6](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/scripts/verify-vsix.js#L6) |

### mux-syntax-highlighting: textmate-mux/vscode-language-mux/package.json

| Dependency | Role | Purpose | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `vscode-languageclient` | runtime | Launch and connect mux lsp from VSCode. | retain | [textmate-mux/vscode-language-mux/extension.js:4](https://github.com/muxlang/mux-syntax-highlighting/blob/c16ccb5face1582b5fcc6803f6dcefbffa8eb151/textmate-mux/vscode-language-mux/extension.js#L4) |

### Compiler updater additions

These 15 declarations were checked against compiler commit [83446fc](https://github.com/muxlang/mux-compiler/commit/83446fc75d70181380aff9ca4569e57c9771e119). The inventory links to source at that commit rather than `main`. The cited production files did not change after the initial review. The later commit normalizes a Windows path assertion in a launcher test and formats the packaging-script tests. The compiler, updater library and Windows launcher share the update transaction. Internal path dependencies still need versions because `cargo package` rewrites their manifests, even when the helper crates are unpublished.

| Scope | Dependency | Role | Purpose | Verdict |
| --- | --- | --- | --- | --- |
| mux-update/Cargo.toml | `ctrlc` | dependencies | Cancel update safely on interrupt/termination. | retain |
| mux-update/Cargo.toml | `flate2` | dependencies | Decompress release tar.gz archives. | retain |
| mux-update/Cargo.toml | `fs2` | dependencies | Advisory locks for safe file/update replacement. | retain |
| mux-update/Cargo.toml | `semver` | dependencies | Compare installed and released compiler versions. | retain |
| mux-update/Cargo.toml | `serde` | dependencies | Custom JSON deserialization and updater release metadata. | retain |
| mux-update/Cargo.toml | `serde_json` | dependencies | JSON encoding/decoding and LSP JSON transport. | retain |
| mux-update/Cargo.toml | `sha2` | dependencies | SHA-2 digests, SQL authentication and updater archive integrity. | retain |
| mux-update/Cargo.toml | `tar` | dependencies | Extract Unix release archives. | retain |
| mux-update/Cargo.toml | `tempfile` | dependencies | Stage downloads/extraction in private temporary directories. | retain |
| mux-update/Cargo.toml | `ureq` | dependencies | Blocking HTTP client and updater HTTPS downloads. | retain |
| mux-update/Cargo.toml | `zip` | dependencies | Extract Windows release archives with deflate only. | retain |
| mux-windows-launcher/Cargo.toml | `clap` | dependencies | Derive CLI argument parsers. | retain |
| mux-windows-launcher/Cargo.toml | `mux-update` | dependencies | Share updater across Unix compiler and Windows launcher. | retain |
| mux-windows-launcher/Cargo.toml | `windows-sys` | dependencies cfg(windows) | Windows file replacement, console or synchronization APIs. | retain |
| mux-compiler/Cargo.toml | `mux-update` | dependencies | Compiler update command shares the transactional updater. | retain |

## Validation and delivery

Changes were prepared in isolated branches. Repo-specific pull requests link the changes and their validation below.

| Candidate | Evidence |
| --- | --- |
| [mux-website PR #118](https://github.com/muxlang/mux-website/pull/118) | Clean npm ci --ignore-scripts; eight unused declarations removed, two formerly hoisted imports declared directly. Lint and TypeScript checks passed. Canonical online syntax parity passed. All 30 test files / 104 tests passed, including local search indexing and client behavior. Production Docusaurus build passed with supported Node 24.21.0. The final 4.1.12 patch passed clean npm ci, lint, typecheck and the same 104 tests with coverage. Search-plugin coverage was 86.14% lines / 70.07% branches. Existing npm advisory gate passes with exactly the 19 pre-approved braces paths and no moderate findings. The regenerated root lock has 76 fewer package entries; retained version changes are the matched Vitest subtree. Production build after the final patch passed under Node 24.21.0. |
| [mux-compiler PR #475](https://github.com/muxlang/mux-compiler/pull/475) | cargo update --workspace --offline removed TOML and five orphan helper entries, upgraded zero packages. cargo fmt --all -- --check passed. MySQL patch upgrades subsequently removed both advisory-warning paths. All five obsolete advisory ignores were removed; ignore is now empty. cargo metadata --locked --offline, cargo audit --no-fetch and cargo-deny advisories/licenses/bans/sources passed. Formatting passed. All-target/all-feature Clippy with -D warnings passed against this lock. Focused SQL validation passed 52 tests (17 library, seven driver, 28 SQL-unit matches) using an isolated copy of the exact pinned runtime source. Cargo cannot test a dependency outside the compiler workspace. The copied lock added only test benchmark dependencies; all shared crate sources/checksums and MySQL/derive/LRU versions matched the compiler candidate. This was offline validation, not a live MySQL/PostgreSQL/SQL Server deployment test. |
| [mux-syntax-highlighting PR #51](https://github.com/muxlang/mux-syntax-highlighting/pull/51) | npm check, VSCode client tests, VSIX packaging/verification passed. Hidden Open VSX lock audit changed from eight high paths to zero. |
| [tree-sitter-mux PR #46](https://github.com/muxlang/tree-sitter-mux/pull/46) | npm check, two highlighted samples, parser generation with no generated drift, and all 46 corpus cases passed. Audit changed from one high path to zero. |
| mux-context docs/dependency-audit | python3 scripts/ci/check-docs.py --repository mux-context passed; all six script unit tests passed. |

The production build used Node 24.21.0 with access to the SWC native binding cache. Syntax parity used the canonical online matrix.

### Newly explicit website imports

| Scope | Dependency | Evidence | Decision |
| --- | --- | --- | --- |
| Root website build | js-yaml >=4.2.0 <5.0.0 | docusaurus.config.ts:4 imports load | Declare directly using the existing approved override range; keep locked 4.3.2. |
| Local search plugin | tslib ^2.8.1 | lib/server/index.js:5 and other generated files require tslib | Declare generated helpers directly; keep locked 2.8.1. |

Remaining work is limited to upstream website braces repair, follow-up review of stale runtime policy comments/ignores on an isolated branch, and merged compiler integration/release validation. Focused lock-dependent SQL validation is complete. No public stdlib API, request sandbox, rate control, CORS boundary, TLS root contract or registry credential check was removed. The existing runtime working branch was not edited. The updater and standalone compiler lock PRs must both be integrated before releasing 0.15.
