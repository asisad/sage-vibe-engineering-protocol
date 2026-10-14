---
name: rust-engineering
description: Use for Rust implementation, reviews, high-performance services, performance-sensitive components and MCP services when selected by the task.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# rust-engineering

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Inspect `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, edition, MSRV and target; preserve existing conventions.
2. If touching an unfamiliar or changing API, consult official Rust docs, docs.rs for the pinned crate release, and package changelog. Record URL/version.
3. Plan ownership, error handling, cancellation, backpressure, bounded memory, Send/Sync, shutdown and metrics overhead.
4. Prefer safe Rust; unsafe blocks and FFI require a documented reason, tests and peer review.
5. Implement small changes and add deterministic tests including cancellation, malformed input, high load and queue saturation when relevant.
6. Validate: `cargo fmt --all -- --check`, `cargo check --workspace --all-targets`, `cargo clippy --workspace --all-targets --all-features -- -D warnings` (adjust incompatible feature combinations), `cargo test --workspace --all-features`.
7. Consider `cargo audit` or equivalent if installed; do not represent that audit as built-in to Cargo. Measure baseline and changed performance before recommending optimization.
8. SENS: reject synchronous telemetry in the application hot path; require fail-open drop/degrade behavior and recursion protection.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
