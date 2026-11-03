# ChangeProof read-only review — 1platformlabs/1platform-api-developer #84

**Prepared:** 2026-11-02 (America/Los_Angeles). **Target:** [issue #84](https://github.com/1platformlabs/1platform-api-developer/issues/84). **Status:** independent triage of publicly accessible evidence, **not a deployed fix**, not an actual customer order, and **not a run of the local proprietary ChangeProof engine**.

## Executive finding

**Confirmed cause in the public repository:** the documentation portal builds from the committed `static/openapi/*.json` files. The workflow `.github/workflows/openapi-drift.yml` detects differences against live API specifications and updates issue #84, but **deliberately does not modify the repository or open a PR**. The `prod.yml` fetch step publishes an artifact rather than updating the tree used by the deployed documentation. Running a deploy for the same commit does not refresh the committed files.

The appropriate fix is a **reviewed PR updating the two versioned OpenAPI JSON files**, followed by the project's required PR checks. The repository explicitly says that merging to `main` triggers production deployment.

## Evidence and source boundaries

The [latest documented measurement](https://github.com/1platformlabs/1platform-api-developer/actions/runs/41566310648) completed successfully and supplied public artifact `openapi-spec-41566310648` (artifact ID `13198842237`). The two files in that artifact were inspected read-only:

| Contract | Live artifact `info.version` | Live operations | Live raw UTF-8 SHA-256 | Bytes |
| --- | --- | ---: | --- | ---: |
| `1platform-api.json` | `PRODv5.122.3` | 893 | `c9b3bccc60d15f09ff3408483613ef0c2c007b0bdc7f007a78833fc3d74f0251` | 6,903,659 |
| `atlas-api.json` | `PRODv0.1.0` | 239 | `61f97308e6466a72ac1c2f4941e48928c85de733f5dceeac8d88065424ef83c8` | 1,269,576 |

**The issue's own comparator** reports the committed `1platform-api` as `PRODv5.94.2` with 788 operations, versus 893 live: 106 additions, one removal, and 786 modified operation JSON objects. The arithmetic is consistent (788 + 106 − 1 = 893). It reports five changed operation objects in `atlas-api` despite its unchanged `info.version`.

The committed large JSON contracts were **not independently retrieved in full** for this review; those before/after counts and detailed comparison results are therefore **attributed to the issue's existing comparator**, not a second ChangeProof engine run.

**Independently inspected in the latest artifact:**
- `DELETE /api/v1/content/competitors/{competitor_id}` is present in the live contract.
- `POST /api/v1/webhooks/mail-provider/inbound` is absent from the live contract. Issue #84 lists it in the committed copy: this is a **contract-level removed operation candidate**, not proof that the running endpoint is inaccessible.
- `GET /api/v1/public/catalog` exists in the live Atlas contract.

**Important classification:** the 786 “changed” operations arise from comparing serialized operation objects in the repository's `scripts/openapi-drift.mjs`. They are **not** 786 independently verified breaking changes. They require categorized schema/parameter/response review before risk labels are assigned. Changes in the five Atlas operations show why unchanged `info.version` is not sufficient to establish contract equality.

## Safe resolution procedure for a maintainer

The existing fetcher is `scripts/fetch-openapi.mjs`, exposed as `pnpm fetch-openapi`. It normally allows a cached fallback when download fails; for a corrective PR, **enable strict mode**, as the drift workflow already does, to avoid treating old cache bytes as refreshed:

```bash
git checkout main
git pull --ff-only
git switch -c docs/refresh-openapi-contracts
pnpm install --frozen-lockfile
OPENAPI_FETCH_STRICT=1 pnpm fetch-openapi
git diff --check
git diff --stat -- static/openapi/
pnpm build
git add static/openapi/1platform-api.json static/openapi/atlas-api.json
git commit -m "docs: refresh published OpenAPI specs"
git push -u origin docs/refresh-openapi-contracts
```

Open a PR into `main`; check that **only the intended published specs** changed and that PR CI/QA succeed. Prioritize a human review of removed `POST /api/v1/webhooks/mail-provider/inbound`, added operations, required input changes, output schemas, and the five Atlas operation diffs. Do **not** merge merely because the build passes. The repository's own documentation notes that merging triggers production publication. No credentials or API invocation are necessary for this read-only process.

After an authorized merge/deploy, let the next scheduled `openapi-drift.yml` check confirm the committed and live contracts match and automatically close #84. Do not close it manually on the basis of this report. As the live API evolves, new drift can appear between fetching the spec and deploying the portal; pin a reviewed artifact or re-check immediately before merge.

## Sources

- [Issue #84 and current comparison](https://github.com/1platformlabs/1platform-api-developer/issues/84)
- [Latest measurement and live OpenAPI artifact](https://github.com/1platformlabs/1platform-api-developer/actions/runs/41566310648)
- [Drift workflow](https://github.com/1platformlabs/1platform-api-developer/blob/main/.github/workflows/openapi-drift.yml)
- [Read-only drift comparison algorithm](https://github.com/1platformlabs/1platform-api-developer/blob/main/scripts/openapi-drift.mjs)
- [Fetcher with strict mode and sanitization](https://github.com/1platformlabs/1platform-api-developer/blob/main/scripts/fetch-openapi.mjs)
- [Production workflow](https://github.com/1platformlabs/1platform-api-developer/blob/main/.github/workflows/prod.yml)

**Limitations:** no access to the target repository's write permissions, no change to its production system, no authenticated runtime requests, no security-sensitive sample data published. A stale public contract is established; actual consumer failures and operation-level compatibility conclusions need targeted tests.
