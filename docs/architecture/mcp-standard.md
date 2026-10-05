# SAGE MCP Standard

An approved MCP integration MUST declare typed tools and schemas, stable names,
capability discovery, dangerous-operation classification, approval policy,
timeout/cancellation, version handshake, an error taxonomy and client
compatibility tests. Prefer typed tools over unrestricted code execution.

Context and token-cost behavior MUST be reviewed. Tool receipts preserve the
resolved scope, authority and evidence references without copying secrets.

Pin an explicitly supported MCP protocol revision. Initialization negotiates
version and capabilities; incompatible responses must fail visibly.
Reference: https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle
(selected reference revision, not a claim that this is the newest revision).
Actual client/server and host receipts are required; descriptor validation is
only a structural check.
