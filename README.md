# ChangeProof

**Know what changed before your AI agent or API client breaks.**

ChangeProof compares two versions of an **MCP `tools/list` definition** or an **OpenAPI contract** and produces a structured, evidence-backed compatibility review. It is designed for maintainers, integration engineers, and developers who need to understand changes to tool interfaces before relying on them.

**[Request a free compatibility pilot](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot)** · **[See a real public-contract case](./ChangeProof_UniFi_68_Validated_Pilot_Report.md)** · **[View a synthetic sample report](./ChangeProof_Sample_Compatibility_Report.md)**

> **Current status — supervised pilot (November 2026).** The existing website supports a pilot request and owner-review workflow; analysis runs through an owner-operated local ChangeProof instance. This is **not** a public self-service analysis API, hosted unattended processing service, or live automated payment system. Requests and delivery are reviewed manually.

## Why ChangeProof?

An API endpoint can remain online while its contract changes. An MCP tool can keep its name while adding a required parameter, narrowing an enum, or changing instructions. For a consuming agent or application, these differences matter.

ChangeProof makes **contract-level changes** easier to inspect, prioritize and verify. It does not replace integration tests or prove how a production system behaves.

## What a review covers

| Area | Example findings | What the result means |
| --- | --- | --- |
| **MCP tool surface** | Added/removed tools, changed `inputSchema`, new required arguments, type/enum changes | Potential compatibility impact for tool callers |
| **MCP metadata** | Tool descriptions, hints and annotations changed | A reason for manual review; **not** proof of effective permissions or behavior |
| **OpenAPI** | Added/removed operations, required request fields, changed response properties and referenced schemas | Structural risks to API consumers |
| **Evidence** | Before/after SHA-256, machine-readable findings, explicit scope | A reproducible reference to **submitted artifacts**, not proof of upstream authenticity |
| **Conclusions** | Breaking candidates, review items and uncertainty | Conservative assessment; runtime compatibility remains **untested** unless separately validated |

A single underlying change can produce several technical findings. Reports should distinguish the **main change themes** from the supporting evidence, rather than implying that every finding is an independent failure.

## See the evidence

### Public OpenAPI case — UniFi Network API

**[Read the UniFi 10.4.57 → 11.0.97 compatibility report](./ChangeProof_UniFi_68_Validated_Pilot_Report.md)**

This published investigation highlights changes in switch-stack response shapes, referenced models and enum values, with hashes, specific schema paths and proposed consumer tests.

**Scope:** analysis of supplied public contract artifacts. This is **not** a claim of a paying customer engagement, production failure or vendor endorsement.

### Synthetic MCP / OpenAPI example

**[Read the sample compatibility report](./ChangeProof_Sample_Compatibility_Report.md)**

An illustrative result using synthetic definitions. It shows how findings and limitations are presented; it is **not external customer validation**.

## How the supervised pilot works

1. **Submit a request:** describe one concrete compatibility question through the [website pilot form](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot).
2. **Identify two revisions:** provide links to two public or sanitized **BEFORE** and **AFTER** definitions, or discuss the scope first. For MCP, a relevant `tools/list` JSON snapshot is suitable; for OpenAPI, JSON or YAML may be suitable.
3. **Owner checks scope and authorization:** input suitability and permission to share the material are reviewed before processing.
4. **Local comparison:** the operator runs the existing ChangeProof workflow and checks the evidence, risk classification and limitations.
5. **Report review and delivery:** findings are reviewed before any external delivery. Submitting a request does not automatically launch an analysis, create an order or send a report.

**Alternative for public GitHub discussions:** [open a free-pilot issue](https://github.com/jajazpua/ChangeProof/issues/new?template=pilot-request.yml). GitHub Issues are public: **never include secrets or nonpublic contracts**.

## What we need — and what we do not

**Useful:** a clear compatibility question, the relevant tool or operation, two revision identifiers and public/sanitized source files or URLs.

**Not needed:** GitHub access, production system access, API tokens, user data, wallet keys, deployment credentials, or remote execution privileges.

The analysis is based on supplied definitions. SHA-256 confirms the bytes being compared, **not** the trustworthiness of their origin. Schema differences alone cannot establish runtime behavior, authentication correctness, side-effect safety or a guaranteed client failure.

## Commercial availability

A free, manually supervised compatibility review may be available for a focused public/sanitized case, subject to scope and capacity.

For larger work, [request a manual quote](https://github.com/jajazpua/ChangeProof/issues/new?template=quote-request.yml). Scope, timing, price and payment method must be agreed independently **before** any paid work. There is no live production checkout, unattended paid MCP endpoint or verified production USDC settlement.

## Repository scope

This repository is the **public product overview, evidence index and pilot contact point**. It does not distribute the proprietary local ChangeProof backend, model, keys, database or production infrastructure. No license for unpublished code is implied.

---

**Have an MCP or OpenAPI change worth checking?** [Request a free compatibility pilot](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot) using public or sanitized contracts.
