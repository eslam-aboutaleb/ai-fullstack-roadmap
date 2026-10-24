"""Runtime type annotation vs boundary enforcement harness.

Demonstrates that Python type annotations are purely advisory metadata for static
analyzers (e.g., Mypy, Pyright) and provide ZERO runtime enforcement by default.
Unchecked boundary inputs (such as parsed JSON or query params) cause silent semantic
bugs (e.g., string concatenation instead of addition) or late runtime crashes far from the call site.
"""

from __future__ import annotations

import functools
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple, Type, get_type_hints


class RuntimeTypeValidationError(TypeError):
    """Raised when runtime inputs violate declared type annotations."""
    pass


def unvalidated_calculate_charge(amount: int, fee: int) -> int:
    """Standard Python function with type hints.

    Python runtime executes this without checking types!
    If amount and fee are strings, '+' concatenates them instead of adding.
    """
    return amount + fee


def enforce_runtime_types(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that validates arguments against declared type annotations at runtime."""
    hints = get_type_hints(func)
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for param_name, param_value in bound.arguments.items():
            expected_type = hints.get(param_name)
            if expected_type is not None:
                # Handle basic primitive types for demonstration
                if isinstance(expected_type, type) and not isinstance(param_value, expected_type):
                    raise RuntimeTypeValidationError(
                        f"Parameter '{param_name}' expected type {expected_type.__name__}, "
                        f"got {type(param_value).__name__} (value: {param_value!r})"
                    )

        result = func(*args, **kwargs)

        return_type = hints.get("return")
        if return_type is not None and isinstance(return_type, type):
            if not isinstance(result, return_type):
                raise RuntimeTypeValidationError(
                    f"Return value expected type {return_type.__name__}, got {type(result).__name__}"
                )

        return result

    return wrapper


@enforce_runtime_types
def validated_calculate_charge(amount: int, fee: int) -> int:
    """Enforced runtime contract: guarantees integer arithmetic."""
    return amount + fee


def run_test_suite() -> None:
    # 1. Demonstrate standard Python lack of runtime enforcement:
    # Notice: strings are passed into a function annotated as int:
    unvalidated_result = unvalidated_calculate_charge("100", "25")  # type: ignore[arg-type]

    # BUG: String concatenation instead of integer sum (semantic data corruption):
    assert unvalidated_result == "10025", "Python silently permitted string concatenation!"
    assert isinstance(unvalidated_result, str)

    # 2. Demonstrate enforced runtime boundary:
    caught_error = False
    try:
        validated_calculate_charge("100", "25")  # type: ignore[arg-type]
    except RuntimeTypeValidationError as err:
        caught_error = True
        assert "Parameter 'amount' expected type int, got str" in str(err)

    assert caught_error is True, "Boundary decorator must reject string arguments"

    # 3. Valid integer inputs succeed as intended:
    valid_result = validated_calculate_charge(100, 25)
    assert valid_result == 125
    assert isinstance(valid_result, int)

    print("All runtime type validation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
