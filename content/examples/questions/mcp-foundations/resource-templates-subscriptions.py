"""MCP Resource URIs, dynamic templates, subscriptions, and tenant identity mapping.

Demonstrates:
1. Fixed resources (resources/list) and RFC 6570 parameterized URI templates (resources/templates/list).
2. Resource reading (resources/read) returning typed text/blob payloads with accurate MIME types.
3. Reactive subscriptions (resources/subscribe) and notifications/resources/updated push notifications.
4. Tenant-scoped authorization mapping: Ensuring client identity restricts resource visibility.
"""
from typing import Any, Dict, List, Optional, Set, Tuple
import re

class McpResourceManager:
    def __init__(self):
        # In-memory document store partitioned by tenant_id
        self._store: Dict[str, Dict[str, Any]] = {
            "file:///tenant_1/security_policy.md": {
                "tenant_id": "tenant_1",
                "mimeType": "text/markdown",
                "text": "# Security Policy\nEnforce MFA on all accounts."
            },
            "file:///tenant_2/security_policy.md": {
                "tenant_id": "tenant_2",
                "mimeType": "text/markdown",
                "text": "# Tenant 2 Internal Draft"
            }
        }
        # Registered URI templates
        self._templates = [
            {
                "uriTemplate": "doc://{tenant_id}/item/{item_id}",
                "name": "Parameterized Item Document",
                "mimeType": "application/json"
            }
        ]
        # Active client subscriptions: uri -> set of client_ids
        self._subscriptions: Dict[str, Set[str]] = {}

    def list_resources(self, caller_tenant_id: str) -> List[Dict[str, Any]]:
        # Filter resources by caller tenant boundary
        return [
            {"uri": uri, "name": uri.split("/")[-1], "mimeType": meta["mimeType"]}
            for uri, meta in self._store.items()
            if meta["tenant_id"] == caller_tenant_id
        ]

    def list_templates(self) -> List[Dict[str, Any]]:
        return self._templates

    def read_resource(self, uri: str, caller_tenant_id: str) -> Dict[str, Any]:
        # Handle dynamic URI template resolution
        template_match = re.match(r"^doc://([^/]+)/item/([^/]+)$", uri)
        if template_match:
            doc_tenant, item_id = template_match.groups()
            if doc_tenant != caller_tenant_id:
                raise PermissionError(f"Access denied: Caller {caller_tenant_id} cannot read tenant {doc_tenant}")
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": f'{{"item_id": "{item_id}", "tenant": "{doc_tenant}", "status": "ACTIVE"}}'
                    }
                ]
            }

        # Handle static resource lookup
        if uri not in self._store:
            raise KeyError(f"Resource not found: {uri}")

        meta = self._store[uri]
        if meta["tenant_id"] != caller_tenant_id:
            raise PermissionError(f"Access denied: Caller {caller_tenant_id} cannot read resource belonging to {meta['tenant_id']}")

        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": meta["mimeType"],
                    "text": meta["text"]
                }
            ]
        }

    def subscribe(self, uri: str, client_id: str, caller_tenant_id: str) -> bool:
        # Verify access before granting subscription
        self.read_resource(uri, caller_tenant_id)
        if uri not in self._subscriptions:
            self._subscriptions[uri] = set()
        self._subscriptions[uri].add(client_id)
        return True

    def update_resource(self, uri: str, new_text: str) -> List[Dict[str, Any]]:
        if uri in self._store:
            self._store[uri]["text"] = new_text

        # Generate notifications/resources/updated frames for subscribed clients
        notifications = []
        if uri in self._subscriptions:
            for client_id in self._subscriptions[uri]:
                notifications.append({
                    "jsonrpc": "2.0",
                    "method": "notifications/resources/updated",
                    "params": {"uri": uri},
                    "target_client": client_id
                })
        return notifications

if __name__ == "__main__":
    mgr = McpResourceManager()

    # 1. Tenant-scoped resource discovery
    t1_resources = mgr.list_resources("tenant_1")
    assert len(t1_resources) == 1
    assert t1_resources[0]["uri"] == "file:///tenant_1/security_policy.md"

    # 2. Reading authorized resource
    read_res = mgr.read_resource("file:///tenant_1/security_policy.md", caller_tenant_id="tenant_1")
    assert "Enforce MFA" in read_res["contents"][0]["text"]
    assert read_res["contents"][0]["mimeType"] == "text/markdown"

    # 3. Cross-tenant access denied
    try:
        mgr.read_resource("file:///tenant_2/security_policy.md", caller_tenant_id="tenant_1")
        assert False, "Should have raised PermissionError"
    except PermissionError as e:
        assert "Access denied" in str(e)

    # 4. Parameterized template reading
    dyn_res = mgr.read_resource("doc://tenant_1/item/item_88", caller_tenant_id="tenant_1")
    assert "item_88" in dyn_res["contents"][0]["text"]

    # 5. Reactive subscription and notification trigger
    mgr.subscribe("file:///tenant_1/security_policy.md", client_id="ide_client_1", caller_tenant_id="tenant_1")
    update_notifications = mgr.update_resource("file:///tenant_1/security_policy.md", "# Updated Security Policy")
    assert len(update_notifications) == 1
    assert update_notifications[0]["method"] == "notifications/resources/updated"
    assert update_notifications[0]["params"]["uri"] == "file:///tenant_1/security_policy.md"
    assert update_notifications[0]["target_client"] == "ide_client_1"

    print("MCP Resource URIs, dynamic templates, and subscriptions verified successfully.")

