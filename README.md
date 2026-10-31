# ChangeProof

**Compatibility preflight for MCP tools, OpenAPI contracts, and AI-agent integrations.**

Detect potentially breaking changes **before** an agent or integration relies on a changed tool definition.

> **Status: Free, supervised pilot.** ChangeProof currently runs as a locally operated prototype. There is no public API endpoint or production payment service available from this repository.

**See a sample output:** [ChangeProof compatibility report — MCP + OpenAPI](./ChangeProof_Sample_Compatibility_Report.md) · 3 MCP findings and 5 OpenAPI findings from **synthetic test fixtures**. This is an illustrative product demonstration, not an external customer result.

## The problem

AI agents depend on tool and API contracts that evolve. A renamed parameter, removed field, newly required input, or changed response schema can break an integration even when the server is still online.

ChangeProof helps developers review those contract changes *before deployment or use*.

## What ChangeProof does

- Compares two **customer-supplied** versions of an MCP tool definition or OpenAPI contract.
- Identifies relevant structural changes and flags **potential** compatibility risks.
- Produces structured, machine-readable findings for developers and automated workflows.
- Includes SHA-256 hashes for comparing and tracking submitted definitions and reports.
- Exposes a local API with service discovery and an OpenAPI 3.1 description.

### Example: a potentially breaking MCP change

**Before (illustrative):**
```json
{
  "name": "search_documents",
  "inputSchema": {
    "type": "object",
    "properties": {"query": {"type": "string"}},
    "required": ["query"]
  }
}
```

**After (illustrative):**
```json
{
  "name": "search_documents",
  "inputSchema": {
    "type": "object",
    "properties": {"search_text": {"type": "string"}},
    "required": ["search_text"]
  }
}
```

Existing clients sending `query` may no longer work. This is an *illustrative example*, not the output of a live ChangeProof run.

## Who this is for

- **MCP server maintainers** evolving their tools.
- **AI-agent developers** integrating external tools.
- **API teams** updating OpenAPI specifications.
- **CI/CD engineers** evaluating whether contract changes merit review.

## Join the free pilot

I am looking for **three developers** who can share a real compatibility problem using **public or sanitized** MCP/OpenAPI definitions.

1. Prepare two self-contained versions of a definition: **before** and **after**.
2. [Open a pilot request](https://github.com/jajazpua/ChangeProof/issues/new?template=pilot-request.yml) describing the problem. **Do not post private schemas or secrets in a public issue.**
3. I will review the example, run a supervised local comparison where feasible, and share structured findings and a short explanation.
4. Tell me what was useful, what was missing, and whether you would use this in your workflow.

You can also join the [ChangeProof pilot conversation on Reddit](https://www.reddit.com/r/ChatGPTCoding/comments/1xfql6y/comment/19rvba0l0kd39/).

**No wallet, API key, credentials, or payment required for the pilot.**

## Current capabilities and limitations

| Area | Current status |
| --- | --- |
| Local service discovery / OpenAPI | Tested locally |
| Preparation of contract comparisons | Tested locally |
| Machine-readable reports and hashes | Implemented in the prototype |
| x402 negotiation | Tested locally on Base Sepolia |
| Production USDC payments | **Not enabled or validated** |
| Public hosted API | **Not available** |
| Independent external customer validation | **Seeking pilot users** |

**Important:** ChangeProof compares submitted definitions. It does **not** authenticate their upstream source, guarantee runtime behavior, or establish that a tool is safe to execute. Static contract checks are one part of a broader integration review. A hash provides an integrity reference; it does not prove that the upstream API is trustworthy.

## Security and privacy

- Send **only public or sanitized** schema examples.
- Never share API keys, wallet keys, seed phrases, access tokens, private endpoints, or confidential customer data.
- The developer-operated pilot does not require remote access to your system.
- No local service port needs to be opened to the internet.

## Project and licensing status

This repository is a **public product overview and pilot contact point**, not the proprietary ChangeProof backend source distribution. No open-source license or commercial license is granted for unpublished code through this page.

---

**Have an MCP or OpenAPI update that might break an AI agent?** [Request a free compatibility check](https://github.com/jajazpua/ChangeProof/issues/new?template=pilot-request.yml).
