"""Framework-Agnostic Hexagonal Architecture (Ports & Adapters) for AI Systems.

Demonstrates:
1. Hexagonal Architecture (Isolation from Framework Churn):
   - Domain Core (`AccountService`) contains 100% of business logic and database persistence;
     has zero imports of LangChain or any external AI framework.
   - Secondary Port (`AiAssistantPort`): abstract interface defining model operations.
2. Interchangeable Adapters:
   - `LangChainAdapter`: wraps model calls in LangChain-style chain abstractions.
   - `NativeClientAdapter`: uses raw vendor client functions without framework abstractions.
3. Zero-Downtime Migration / Framework Replacement:
   - Replaces the LangChain adapter with the Native adapter without altering a single line
     of domain business rules, database queries, or public REST API contracts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import time
from typing import Any, Dict, Optional


# ==========================================
# 1. CORE DOMAIN LAYER (Zero Framework Imports)
# ==========================================

@dataclass
class AccountRecord:
    account_id: str
    owner_name: str
    balance: float
    tier: str


class AccountDomainService:
    """Pure business domain service. Completely isolated from any AI framework."""

    ACCOUNTS = {
        "ACC-001": AccountRecord("ACC-001", "Acme Logistics", 14500.0, "ENTERPRISE"),
        "ACC-002": AccountRecord("ACC-002", "Beta Retail", 320.0, "STANDARD")
    }

    @classmethod
    def get_account(cls, account_id: str) -> AccountRecord:
        acct = cls.ACCOUNTS.get(account_id)
        if not acct:
            raise KeyError(f"Account {account_id} not found")
        return acct

    @classmethod
    def calculate_credit_limit(cls, account: AccountRecord) -> float:
        """Deterministic business rule."""
        multiplier = 2.5 if account.tier == "ENTERPRISE" else 1.2
        return round(account.balance * multiplier, 2)


# ==========================================
# 2. APPLICATION PORT (Interface Definition)
# ==========================================

class AiAssistantPort(ABC):
    """Abstract Port: Application calls this interface; knows nothing of LangChain."""

    @abstractmethod
    def generate_executive_briefing(self, account: AccountRecord, credit_limit: float) -> str:
        pass


# ==========================================
# 3. ADAPTER A: LangChain-Style Adapter
# ==========================================

class LangChainFrameworkAdapter(AiAssistantPort):
    """Adapter implementing port using LangChain abstractions (runnables, chains)."""

    def __init__(self, model_name: str = "lc-gpt-4o"):
        self.model_name = model_name

    def generate_executive_briefing(self, account: AccountRecord, credit_limit: float) -> str:
        # Simulates: prompt | model | parser pipeline
        framework_metadata = {"framework": "LangChain", "runnable_id": "chain_briefing_v1"}
        briefing = (
            f"Executive Briefing for {account.owner_name} ({account.tier}): "
            f"Current Balance is ${account.balance:,.2f}. "
            f"Approved Credit Limit: ${credit_limit:,.2f}."
        )
        return briefing


# ==========================================
# 4. ADAPTER B: Native Python Client Adapter (Framework Replacement)
# ==========================================

class NativePythonClientAdapter(AiAssistantPort):
    """Adapter implementing port using lightweight native Python client (no LangChain)."""

    def __init__(self, model_name: str = "native-client-v1"):
        self.model_name = model_name

    def generate_executive_briefing(self, account: AccountRecord, credit_limit: float) -> str:
        # Directly formats request and parses model response with zero framework overhead
        briefing = (
            f"Executive Briefing for {account.owner_name} ({account.tier}): "
            f"Current Balance is ${account.balance:,.2f}. "
            f"Approved Credit Limit: ${credit_limit:,.2f}."
        )
        return briefing


# ==========================================
# 5. APPLICATION SERVICE (Orchestration)
# ==========================================

class EnterpriseAccountController:
    """Public controller orchestrating domain service and AI Port."""

    def __init__(self, domain_service: AccountDomainService, ai_assistant: AiAssistantPort):
        self.domain = domain_service
        self.ai_assistant = ai_assistant

    def handle_account_inquiry(self, account_id: str) -> Dict[str, Any]:
        # 1. Authoritative domain business logic
        account = self.domain.get_account(account_id)
        credit_limit = self.domain.calculate_credit_limit(account)

        # 2. AI Port invocation (Hexagonal decoupled call)
        briefing = self.ai_assistant.generate_executive_briefing(account, credit_limit)

        # 3. Stable public API response contract
        return {
            "account_id": account.account_id,
            "owner": account.owner_name,
            "tier": account.tier,
            "balance": account.balance,
            "credit_limit": credit_limit,
            "briefing": briefing
        }


def main():
    domain_service = AccountDomainService()

    # 1. Run with LangChain Adapter
    print("1. Enterprise Controller running with LangChain Adapter:")
    lc_adapter = LangChainFrameworkAdapter()
    controller_lc = EnterpriseAccountController(domain_service, lc_adapter)
    resp_lc = controller_lc.handle_account_inquiry("ACC-001")

    print(f"  Account ID: {resp_lc['account_id']}")
    print(f"  Credit Limit: ${resp_lc['credit_limit']:,.2f}")
    print(f"  Briefing: {resp_lc['briefing']}")

    assert resp_lc["credit_limit"] == 36250.0  # 14500 * 2.5
    assert "Acme Logistics" in resp_lc["briefing"]

    # 2. Zero-Downtime Migration to Native Adapter (Zero Framework Churn)
    print("\n2. Migrating to Native Client Adapter (Zero changes to domain service or public API):")
    native_adapter = NativePythonClientAdapter()
    controller_native = EnterpriseAccountController(domain_service, native_adapter)
    resp_native = controller_native.handle_account_inquiry("ACC-001")

    print(f"  Account ID: {resp_native['account_id']}")
    print(f"  Credit Limit: ${resp_native['credit_limit']:,.2f}")
    print(f"  Briefing: {resp_native['briefing']}")

    # 3. Verify Exact Contract Parity
    assert resp_lc["account_id"] == resp_native["account_id"]
    assert resp_lc["credit_limit"] == resp_native["credit_limit"]
    assert resp_lc["briefing"] == resp_native["briefing"]

    print("\nFramework-agnostic hexagonal architecture and zero-churn replacement verified successfully.")


if __name__ == "__main__":
    main()

