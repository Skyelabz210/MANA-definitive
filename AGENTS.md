# Repository Guidelines

## Project Structure & Module Organization
- `crates/nine65/` is the core FHE library; implementation modules live under `crates/nine65/src/` (e.g., `arithmetic/`, `ops/`, `quantum/`, `noise/`).
- `crates/mana/` provides modular arithmetic acceleration used by `nine65`.
- `crates/unhal/` contains the hardware abstraction layer and pipeline helpers.
- Benchmark examples live in `crates/mana/examples/benchmark.rs` and `crates/unhal/examples/unhal_benchmark.rs`.
- `docs/` holds design and security notes; `target/` contains build and benchmark artifacts.

## Build, Test, and Development Commands
- `cargo build --workspace` builds all crates in the workspace.
- `cargo test --workspace` runs unit tests across crates.
- `cargo test -p nine65 --features v2 v2_integration` runs the v2 integration suite.
- `cargo run --release --example benchmark -p mana` runs the MANA benchmark example.
- `cargo run --release --example unhal_benchmark -p unhal` runs the UNHAL benchmark example.
- `cargo bench -p nine65` or `cargo bench -p mana` runs Criterion benchmarks defined in each crate.

## Coding Style & Naming Conventions
- Rust 2021 edition; use standard rustfmt defaults (4-space indentation).
- Files and modules use `snake_case`; types/traits use `CamelCase`; constants use `SCREAMING_SNAKE_CASE`.
- Keep math-heavy code explicit; add brief comments only when the intent is not obvious from the math or naming.

## Testing Guidelines
- Unit tests live next to the modules they cover (`#[cfg(test)]`).
- Integration-style tests are in `crates/nine65/src/v2_integration_tests.rs`.
- Property-based testing uses `proptest`; benchmarks use `criterion` (see each crate `Cargo.toml`).

## Solo Workflow & Internal Audit
- This is a private, solo codebase; no external contribution or PR process is expected.
- Keep local commits short and descriptive (e.g., "Tighten RNS bounds") so audit trails stay readable.
- Before an audit pass, record the exact feature flags used (e.g., `--features v2,parallel`).

## Independent Audit Checklist
- Start with `docs/SECURITY_PROOFS.md` to align on assumptions and security targets.
- Review core math paths in `crates/nine65/src/arithmetic/` and `crates/nine65/src/ops/` for bounds and constant-time expectations.
- Verify randomness and key handling in `crates/nine65/src/entropy/` and `crates/nine65/src/keys/`; confirm `zeroize` usage where secrets are dropped.
- Re-run tests and benchmarks with the same flags used in release builds; save results alongside `docs/`.

## Security & Configuration Notes
- Security reasoning and performance comparisons live in `docs/SECURITY_PROOFS.md` and `docs/FHE_BENCHMARK_COMPARISON.md`.
- Treat key material and RNG use as sensitive; avoid logging secrets and prefer `zeroize` for cleanup.
