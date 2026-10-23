# MCP interoperability and remote authorization exercise (#47)

Intro: MCP hosts, client instances and servers negotiate protocol/capabilities,
but only a trusted host/application can grant concrete tool authority.
Resources and tool result text are **data**, not system instructions.

Run python3 -B labs/mcp_remote_policy.py to test protocol-version
intersection, issued-resource audience, expiry, scoped read/write tools,
human approval and replay rejection.

SECURITY LIMIT: this is a **policy-only fixture** with already-verified
synthetic identity records, not OAuth/OIDC cryptographic verification.
A real remote service must pin SDK/spec versions, verify discovery metadata,
JWT/signature/JWKS issuer/algorithm/audience, implement browser PKCE/state,
test HTTP origin/SSRF and denial flows, and persist its effect journal.
The existing official SDK protocol-interoperability lab covers local behavior;
cross-vendor/remote OAuth are independently unverified tasks.
