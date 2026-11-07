# Immich #28325: a scoped OpenAPI enum-removal review

[ChangeProof overview](../../README.md) · [Public evidence index](../../docs/PUBLIC_EVIDENCE.md) · [Upstream PR #28325](https://github.com/immich-app/immich/pull/28325)

**One public contract change, two affected request fields.** An offline ChangeProof staging run identified the removal of the deprecated `libopus` value from `AudioCodec`. The `opus` value remains available.

This is an independent technical sample based on public source, not a customer engagement, Immich endorsement, production deployment or demonstration of a live failure.

## What changed

The compared file is `open-api/immich-openapi-specs.json`:

- **Before:** [`eea820fa2f441953bf363179bb18394dbd56b713`](https://github.com/immich-app/immich/blob/eea820fa2f441953bf363179bb18394dbd56b713/open-api/immich-openapi-specs.json#L16927-L16937), the parent of the merged change.
- **After:** [`d788169bf3333cb5f075482c4eb66ee16c262e16`](https://github.com/immich-app/immich/blob/d788169bf3333cb5f075482c4eb66ee16c262e16/open-api/immich-openapi-specs.json#L16927-L16936).

Removing `libopus` from `AudioCodec.enum` is the only difference in the parsed full JSON documents. This retires an old contract value; it does not remove Opus support.

## Scope and recorded result

The analysis covered **PUT /api/system-config**: the specification's `/system-config` operation with server base `/api`, plus its complete closure of **48 referenced schemas**. The operation, schemas and security definitions were preserved without schema edits. The comparison did not cover every operation across the full specification's 159 paths.

The recorded ChangeProof `1.1.0rc9.dev1` staging run reported:

- **Two request-side breaking candidates:** `ffmpeg.targetAudioCodec` and each item in `ffmpeg.acceptedAudioCodecs`.
- **Two response-side review locations** for the same fields.
- Risk exit code **3** for JSON and SARIF output.
- Exit code **0** and no changes for the identical-input control.

These locations trace **one underlying enum removal**, not multiple independent defects. Existing callers that still use `libopus` warrant migration review and targeted tests.

## Independent checks

A separate source and artifact check, without importing or rerunning ChangeProof, confirmed the source hashes, the 48-schema reference closure and the report's canonical input hashes. Local source bytes also matched the Git blob identifiers returned by GitHub for the pinned revisions.

A `jsonschema.Draft4Validator` check of the simple `AudioCodec` string/enum component confirmed:

| Value | Before | After |
| --- | --- | --- |
| `libopus` | Accepted | Rejected |
| `opus` | Accepted | Accepted |

This is a component-level schema witness, not a complete HTTP request or server test.

Raw SHA-256 of the full source files:

- Before: `e3f002f2e5b553526739a35e96a121a3796b7a30fd88ce7504f2970a36ae640a`
- After: `b6d53c37b0d70ed859936316173e4987da5fc160027d83edb703e0bfa02d8c51`

Hashes identify bytes; they are not digital signatures.

## Limits and follow-up

No Immich server, authentication flow, generated SDK or downstream client was exercised. No production failure, security vulnerability or exhaustive compatibility proof is claimed. Static completeness applies only to the recorded scope.

The original staging SARIF contains stale `v7` and `NOT_INSTALLED` metadata labels. They are a reporting defect; this sample does not present that SARIF as a corrected release artifact.

Review callers and stored configuration that still use `libopus`, then test both affected fields against the intended Immich release.

## Attribution

Source: [Immich](https://github.com/immich-app/immich), PR #28325 by [mertalev](https://github.com/immich-app/immich/pull/28325). Immich's upstream [license at the reviewed revision](https://github.com/immich-app/immich/blob/d788169bf3333cb5f075482c4eb66ee16c262e16/LICENSE) is GNU AGPL v3. This sample links to upstream source rather than redistributing the specification or generated SDKs.