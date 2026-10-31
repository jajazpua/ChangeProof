# ChangeProof — UniFi Network API Compatibility Pilot

**Pilot static-analysis report — validated build (31 October 2026)**

**Assessment:** definition-level compatibility review  
**Baseline:** UniFi Network API 10.4.57  
**Candidate:** UniFi Network API 11.0.97  
**Status:** HIGH-priority compatibility review; **runtime breakage not verified**  
**Audience:** API maintainers and client developers  
**Analysis engine:** ChangeProof V1.0 + OpenAPI semantic-compatibility patch (`openapi-semantic-review-1`)

## Executive summary

ChangeProof detected an OpenAPI contract drift between the two versions and classified **42 findings: 9 HIGH potential risks and 33 REVIEW items**. The headline compatibility concern is a structural migration of switch stack data from a required `members` collection to a required `units` collection. The change also alters the associated data model, so clients expecting the former response shape may require adaptation. These are **contract-definition findings**; they do **not** establish that a particular deployed application fails.

The original comparison produced 14 broad findings; the revised analyzer emitted 42 more granular findings. The counts are not directly comparable as a measurement of quality, and the nine HIGH items include related observations about some of the same underlying migrations.

## Evidence and provenance

The analysis uses the supplied raw `before.json` and `after.json` and the user-provided `semantic_final_review.txt`. The two JSON files have `openapi: 3.1.0` and describe 44 paths each. The baseline declares 379 component schemas; the candidate declares 380.

| Artifact | SHA-256 of supplied raw file |
|---|---|
| UniFi 10.4.57 (`before.json`) | `3773947b4572b1bdc84272d3d2b9ebb5cad0d9aaa2640c3418568df97c9df59d` |
| UniFi 11.0.97 (`after.json`) | `0828aa9f017cce92cd035429c7e19c933d0b3387c561aac17c468b4c2ca8be66` |

These hashes allow exact comparison with the supplied files; they are **not** digital signatures or proof of upstream authenticity. Existing ChangeProof evidence receipts remain separate.

## High-priority compatibility concerns

### 1. Switch stack response representation — high priority

**Schema:** `IntegrationSwitchStackDto`.

- In 10.4.57, `members` is required and is an array of `IntegrationSwitchStackMemberDto` with at least two items. That referenced schema requires `deviceId`.
- In 11.0.97, `members` is absent; `units` is required and is an array of `IntegrationSwitchStackUnitDto` with at least two items. This new item schema requires `id` and `macAddress` and includes `order` and `role`. A `deviceId` property is also newly declared on the outer switch stack schema.
- A parser or generated model that expects `members` may not recognize or correctly expose `units`. The precise application effect depends on the client library and how it handles missing or extra response fields.

**Recommended client test:** deserialize representative switch-stack responses from both versions using the existing generated client, and check whether expected `members`/`units` model attributes are populated or rejected.

### 2. LAG response fields — high priority

**Schema:** `LAG details`.

- The previous schema declares `members` as a required property with array items referencing `IntegrationLagMemberDto`.
- The candidate removes `members` from `properties` and from `required`; no replacement field is declared under the same schema.

**Recommended client test:** check code paths that render, parse, or validate LAG membership from the affected GET operations.

### 3. Local switch-stack LAG member model — high priority

**Schema:** `IntegrationSwitchStackLagLocalDto`.

- The property path `members/items/$ref` changes from `IntegrationLagMemberDto` to `IntegrationSwitchStackLagMemberDto`.
- The new item schema requires `portIdxs`, `unitId`, and `unitMacAddress`.
- The old `IntegrationSwitchStackMemberDto` component is removed, and `IntegrationSwitchStackUnitDto` is added. These should be treated as related migration indicators, not necessarily three independent runtime failures.

**Recommended client test:** regenerate or validate models against the new `$ref` targets, compare serialized fields, and test consumer compatibility.

### 4. Radio enum expansion — high priority for strict clients

The candidate extends two `frequencyGHz` enums with numeric `0.9` and the wireless `wlanStandard` enum with string `802.11ah`. There are no removed values in these three changes. Adding output enum values is not universally breaking, but **strict consumer parsers** or exhaustive branches may reject previously unseen values.

**Recommended client test:** exercise generated clients and consumer logic with the new values. Do not classify the mere existence of these additions as a confirmed break for permissive clients.

## Other reviewed changes

- The response schema `Firewall policy` adds `reportFlowEnabled` as a required boolean field; request-oriented `Create or update firewall policy` and `Patch firewall policy` add the optional field without making it required. Review strict response decoders, but distinguish this from introducing a mandatory request parameter.
- `Wireless radio overview` adds a required response field `txPowerMode`.
- Seven `allOf` composition changes require effective-schema examination after reference resolution; the report currently classifies them as REVIEW.
- Thirteen API operations reference changed schemas. These are contextual links, **not thirteen confirmed failures**.
- The change to the switch-stack GET operation's description is classified separately as `API_OPERATION_DOCUMENTATION_CHANGED` (REVIEW). Documentation alone is not evidence of wire-format incompatibility.

## Findings by class

| Classification | Count |
|---|---:|
| API_REFERENCED_SCHEMAS_CHANGED | 13 |
| API_SCHEMA_COMPOSITION_CHANGED | 7 |
| API_PROPERTY_ADDED | 6 |
| API_REQUIRED_FIELDS_CHANGED | 4 |
| API_ENUM_VALUES_CHANGED | 3 |
| API_SCHEMA_STRUCTURE_CHANGED | 2 |
| API_PROPERTY_REMOVED | 2 |
| API_SCHEMA_ADDED | 2 |
| API_SCHEMA_CONSTRAINT_CHANGED | 1 |
| API_SCHEMA_REMOVED | 1 |
| API_OPERATION_DOCUMENTATION_CHANGED | 1 |
| **TOTAL** | **42** |

**Severity:** 9 HIGH, 33 REVIEW. A HIGH finding is a reason to investigate and test, not an assertion of deployment failure.

## Validation status (31 October 2026)

**Completed on the supplied artifacts:**

- Raw `before.json` and `after.json` parsed successfully; both declare OpenAPI 3.1.0. Exact supplied-file SHA-256 values are recorded above.
- ChangeProof created an isolated baseline, detected contract drift, and produced a machine-readable evidence report.
- Independent inspection compared the values at **30 changed JSON pointers**, including `required`, `enum`, `$ref`, removed fields and schema composition.
- Internal `$ref` resolution check: **520 references inspected in 10.4.57, 524 in 11.0.97, zero unresolved in either file**. This check is not equivalent to full standards validation.
- Semantic triage reproduction: **42 findings — 9 HIGH and 33 REVIEW**; historical evidence verification and the newly added targeted regression tests passed in the isolated patch test environment.
- Operator's Windows environment reports **Windows Encoding: PASS** and **Full Regression: PASS (258 tests executed/discovered)** in `ChangeProof_Final_Validation.txt`. The final short summary does not provide per-test pass/skip totals. This establishes regression-suite success, **not** compatibility of deployed UniFi clients.

**Not completed / not established:**

- **Full OpenAPI 3.1 / JSON Schema standards validation: NOT RUN**. The dedicated validator was unavailable; internal reference checks do not replace it.
- **Runtime client compatibility tests: NOT RUN**. No representative generated SDK/client was executed against fixtures or deployed endpoints.
- No production UniFi calls, real customer-system access, authentication/security audit, or upstream provenance attestation was performed.
- **Live x402/USDC settlement: NOT TESTED**, and unrelated to the static compatibility findings.
- No acceptance or endorsement by UniFi maintainers or a third-party client is claimed.

## Interpretation and practical migration checks

**Priority: HIGH — investigation recommended; not a certified breaking-change finding.** These nine HIGH alerts reflect overlapping contract-definition observations and must not be interpreted as nine independent runtime failures. In particular:

1. Check switch-stack response deserialization and UI logic against the `members` → `units` structure, including `deviceId`, `id`, `macAddress`, `order`, and `role` field expectations.
2. Check whether code that reads LAG `members` relies on a property no longer declared in the candidate schema.
3. Regenerate and compile strict SDK models referencing `IntegrationSwitchStackLagLocalDto`, then test the updated `members/items/$ref` model.
4. Test strict parsers for the added `frequencyGHz = 0.9` and `wlanStandard = "802.11ah"` values.
5. Revisit the seven `allOf` composition changes after effective-schema resolution; currently they are REVIEW rather than confirmed breaking changes.
6. Before claiming full API validity, validate both OpenAPI documents with a dedicated OpenAPI 3.1-compatible standards validator and capture its output.

## Decision

**Suitable to share as an evidence-backed, preliminary technical pilot report** describing high-priority *potential* compatibility risks. It is **not** a certificate of JSON Schema correctness or proof of application breakage. Obtain independent client runtime evidence for any claim that an installed integration actually fails.

**Recommended outreach:** provide the maintainer the exact pair of versioned documents/hashes, focus on the switch-stack `members` → `units` migration, and request an example generated client or sanitized response fixture to test. Do not ask for private tokens, credentials, or production data.

---

*Prepared using supplied raw UniFi specifications, ChangeProof output, independent value-level inspection and the operator’s local regression summary. No live customer systems were accessed.*
