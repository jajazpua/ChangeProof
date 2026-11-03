# ChangeProof / Denkeeper #583 — reproducible synthetic MCP fixture

Prepared 2026-11-02 following [@Temikus's response](https://github.com/Temikus/denkeeper/issues/583#issuecomment-6589624804) to the offer of a free regression example.

**Scope:** synthetic, read-only before/after MCP tools/list JSON. No Denkeeper capture, credentials, live requests, or production execution. This independent verifier **does not execute the proprietary ChangeProof engine**.

## Reproduce

From this directory with Python 3.12 (or a compatible Python 3.x):

    python -m pip install -r requirements.txt
    python verify.py

The recorded local run passed **44 scoped checks** covering seven SHA-256 byte identities, six controlled change scenarios, and four input/output schema witnesses. The verifier has no remote data dependencies. See [REPORT.md](REPORT.md) and [SHA256SUMS.json](SHA256SUMS.json).

## Snapshots

- `before.tools-list.json`: baseline tool `note_update`.
- `description_only.after.tools-list.json`: description changes.
- `annotation_only.after.tools-list.json`: `readOnlyHint: false` becomes `true`.
- `input_required_only.after.tools-list.json`: `approval_code` becomes required.
- `output_enum_only.after.tools-list.json`: adds `queued` status.
- `combined.after.tools-list.json`: all four changes at once.
- `key_order_only.after.tools-list.json`: object key order changes but semantic JSON value does not.

The proposal's proposed digest `(name, description, inputSchema, annotations)` is tested only as a **proposal**: it does not include `outputSchema`. The local sorted-key hash is a narrow test equality control, **not RFC 8785**.

**Not tested:** Denkeeper ingestion, registration, restart, live probe, runtime behavior, permissions, prompt-injection exploit, persistence, audit trail, operator re-pin, or ChangeProof V1.3 execution. No maintainer acceptance or endorsement is implied.
