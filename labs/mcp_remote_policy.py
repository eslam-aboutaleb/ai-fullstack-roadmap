"""Policy-only MCP remote auth/permission reference: NOT a JWT verifier.

Only consume identities after a real OIDC/OAuth library cryptographically
verifies signature, algorithm, issuer metadata, expiry, audience and nonce/PKCE
where relevant. This fixture checks protocol/profile and authorization routing.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Identity:
    issuer: str
    subject: str
    audience: str
    scopes: frozenset
    expires: int

@dataclass(frozen=True)
class Tool:
    name: str
    scope: str
    effect: bool

class Policy:
    def __init__(self, issuer, audience, server_tools, supported_versions):
        self.issuer=issuer;self.audience=audience
        self.tools={tool.name:tool for tool in server_tools}
        self.versions=frozenset(supported_versions)
        self.effects=set()

    def negotiate(self, offered):
        matched=[v for v in offered if v in self.versions]
        if not matched:raise ValueError("unsupported MCP protocol version")
        return sorted(matched)[-1]

    def authorize(self, identity, name, *, now, approved=False, operation=None):
        # The identity is an ALREADY VERIFIED record; never trust arbitrary JSON
        # client claims as identity. Scope and subject must be derived by host.
        if not isinstance(identity,Identity) or not identity.subject:
            raise PermissionError("verified principal required")
        if identity.issuer!=self.issuer or identity.audience!=self.audience:
            raise PermissionError("issuer or resource audience mismatch")
        if now>=identity.expires:raise PermissionError("expired token")
        tool=self.tools.get(name)
        if tool is None:raise ValueError("tool not advertised")
        if tool.scope not in identity.scopes:raise PermissionError("insufficient scope")
        if tool.effect:
            if not approved:raise PermissionError("independent effect approval required")
            if not operation:raise ValueError("effect requires stable operation ID")
            identity_key=(identity.subject,name,operation)
            if identity_key in self.effects:
                return "duplicate-effect-rejected"
            self.effects.add(identity_key)
        return "allowed"

def check():
    tools=[Tool("lookup","read:docs",False),Tool("submit","write:requests",True)]
    policy=Policy("https://issuer.example","https://mcp.example",tools,["2025-11-25","2026-07-28"])
    assert policy.negotiate(["2025-11-25","2026-07-28"])=="2026-07-28"
    try:policy.negotiate(["2021-01-01"])
    except ValueError:pass
    else:raise AssertionError("unsupported protocol accepted")
    principal=Identity("https://issuer.example","user-a","https://mcp.example",
                       frozenset({"read:docs","write:requests"}),1000)
    assert policy.authorize(principal,"lookup",now=100)=="allowed"
    bad=Identity(principal.issuer,principal.subject,"https://other-server",
                 principal.scopes,principal.expires)
    try:policy.authorize(bad,"lookup",now=100)
    except PermissionError:pass
    else:raise AssertionError("wrong audience forwarded")
    read=Identity(principal.issuer,"user-b",principal.audience,
                  frozenset({"read:docs"}),1000)
    try:policy.authorize(read,"submit",now=100,approved=True,operation="x")
    except PermissionError:pass
    else:raise AssertionError("read-only token escalated")
    try:policy.authorize(principal,"submit",now=100,operation="x")
    except PermissionError:pass
    else:raise AssertionError("write without approval")
    assert policy.authorize(principal,"submit",now=100,approved=True,operation="x")=="allowed"
    assert policy.authorize(principal,"submit",now=100,approved=True,operation="x")=="duplicate-effect-rejected"
    try:policy.authorize(principal,"lookup",now=1000)
    except PermissionError:pass
    else:raise AssertionError("expired identity accepted")
    print("MCP policy: version, audience, permission, approval, effect replay PASS")
if __name__=="__main__":check()
