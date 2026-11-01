Hi @Aias00 — thank you. I've prepared the requested small synthetic MCP regression fixture.

The combined before/after pair contains:
- an existing optional input becoming required: an old request can be rejected by the new tool;
- an output enum expansion: a new response can be rejected by a strict old consumer;
- a `readOnlyHint` change, reported separately as advisory metadata requiring review.

The package includes both JSON snapshots, machine-readable structural facts and expected compatibility directions, the actual ChangeProof V1.2.3 findings, and a standalone Python verifier for the structural changes and JSON Schema witnesses. It also includes isolated annotation-only, key-order-only and unsupported-composition controls; the latter is explicitly indeterminate and requires review.

[Insert the verified public artifact-directory URL after publication.]

The verifier is fixture-scoped and public; the commercial ChangeProof engine is not included. Its recorded outputs and module hash are supplied separately. This is a static contract fixture only. Runtime behavior, generation consistency and pinning correctness remain separate acceptance criteria, as you requested.

I'd welcome your review of the expected directions and whether the fixture fits the regression suite for #7935.
