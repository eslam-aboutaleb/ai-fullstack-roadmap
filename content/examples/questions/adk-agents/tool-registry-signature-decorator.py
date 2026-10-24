"""Tool Registry, Function Signature Preservation, and Error Taxonomy.

Demonstrates:
1. Model-Facing Contract Generation:
   - Tool decorator inspects type annotations and docstrings to build strict JSON Schema tool definitions.
   - Preserves inspectable signatures and metadata using `functools.wraps` (defeating wrapper erasure).
2. Returned Tool Errors vs Raised Exceptions:
   - Returned Tool Error (`is_error: True`): expected operational failures (e.g. invalid account ID).
     Returned to model as observation so the model can adjust its strategy and self-correct.
   - Raised Fatal Exception: unrecoverable runtime crashes (e.g., database connection failure).
     Halts execution and logs alerts; never exposed to model for hallucinated retries.
3. Deterministic Validation + Flexible Reasoning:
   - Python tools deterministically enforce regex, boundary, and business constraints before returning clean state.
"""

from dataclasses import dataclass, field
import functools
import inspect
import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, get_type_hints


@dataclass
class ToolExecutionResult:
    is_error: bool
    output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """Registry maintaining model-facing JSON Schemas and dispatch handlers."""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.executables: Dict[str, Callable] = {}

    def register(self, func: Callable) -> Callable:
        # Use inspect to build JSON schema
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""

        properties = {}
        required = []

        type_hints = get_type_hints(func)

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = type_hints.get(param_name, str)
            json_type = "string"
            if param_type == int:
                json_type = "integer"
            elif param_type == float:
                json_type = "number"
            elif param_type == bool:
                json_type = "boolean"
            elif param_type == list or getattr(param_type, "__origin__", None) == list:
                json_type = "array"

            properties[param_name] = {"type": json_type}
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc.split("\n")[0] if doc else "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

        self.tools[func.__name__] = schema
        self.executables[func.__name__] = func
        return func

    def dispatch(self, tool_name: str, arguments: Dict[str, Any]) -> ToolExecutionResult:
        if tool_name not in self.executables:
            return ToolExecutionResult(is_error=True, output=f"Unknown tool '{tool_name}'")

        func = self.executables[tool_name]
        try:
            # Deterministic code execution
            val = func(**arguments)
            return ToolExecutionResult(is_error=False, output=val)
        except ValueError as val_err:
            # Expected domain validation failure: Return error observation so model can recover!
            return ToolExecutionResult(is_error=True, output=f"Validation error: {val_err}")
        except Exception as crash_err:
            # Unhandled infrastructure crash: Re-raise! Must NOT let model guess around hardware crash
            raise RuntimeError(f"FATAL INFRASTRUCTURE EXCEPTION in tool {tool_name}: {crash_err}") from crash_err


# --- Example Instrumented Tools ---
registry = ToolRegistry()


def instrumented_logger(func: Callable) -> Callable:
    """Decorator adding logging while preserving underlying signature with functools.wraps."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # logging side-effect
        return func(*args, **kwargs)
    return wrapper


@registry.register
@instrumented_logger
def calculate_vat_invoice(subtotal: float, country_code: str) -> Dict[str, Any]:
    """Calculate VAT rate and total amount for cross-border invoicing.

    subtotal: Net amount in EUR before tax
    country_code: Two-letter ISO country code (e.g. DE, FR, US)
    """
    # Deterministic validation
    if subtotal <= 0:
        raise ValueError("Subtotal must be greater than zero")

    country_clean = country_code.upper().strip()
    rates = {"DE": 0.19, "FR": 0.20, "GB": 0.20, "US": 0.00}
    if country_clean not in rates:
        raise ValueError(f"Unsupported country code '{country_code}'. Supported: {sorted(rates.keys())}")

    rate = rates[country_clean]
    vat_amount = round(subtotal * rate, 2)
    return {
        "subtotal": subtotal,
        "country": country_clean,
        "vat_rate": rate,
        "vat_amount": vat_amount,
        "total": round(subtotal + vat_amount, 2)
    }


def main():
    # 1. Verify Signature Preservation
    print("1. Signature and Schema Inspection:")
    schema = registry.tools["calculate_vat_invoice"]
    print(json.dumps(schema, indent=2))

    # Assert that signature was preserved despite the @instrumented_logger wrapper!
    sig = inspect.signature(registry.executables["calculate_vat_invoice"])
    assert "subtotal" in sig.parameters
    assert "country_code" in sig.parameters
    assert schema["function"]["parameters"]["required"] == ["subtotal", "country_code"]

    # 2. Test Successful Deterministic Execution
    print("\n2. Successful Tool Dispatch:")
    res_success = registry.dispatch("calculate_vat_invoice", {"subtotal": 100.0, "country_code": "DE"})
    print(f"  Result (is_error={res_success.is_error}): {res_success.output}")
    assert res_success.is_error is False
    assert res_success.output["vat_amount"] == 19.0

    # 3. Test Returned Tool Error (Model Self-Correction Opportunity)
    print("\n3. Returned Tool Error (Domain Validation Failure):")
    res_error = registry.dispatch("calculate_vat_invoice", {"subtotal": 100.0, "country_code": "JP"})
    print(f"  Result (is_error={res_error.is_error}): {res_error.output}")
    assert res_error.is_error is True
    assert "Unsupported country code" in res_error.output

    # 4. Test Raised Exception vs Returned Error
    print("\n4. Raised Infrastructure Exception (Fatal Crash):")
    @registry.register
    def failing_db_tool(query: str) -> str:
        """Query database with mock connection failure."""
        raise ConnectionResetError("Connection reset by peer (TCP RST received from database cluster)")

    try:
        registry.dispatch("failing_db_tool", {"query": "SELECT *"})
        assert False, "Fatal infrastructure exception must be re-raised"
    except RuntimeError as fatal_err:
        print(f"  Successfully re-raised fatal infrastructure exception: {fatal_err}")
        assert "FATAL INFRASTRUCTURE EXCEPTION" in str(fatal_err)

    print("\nTool registry schema generation, signature preservation, and error taxonomy verified successfully.")


if __name__ == "__main__":
    main()
