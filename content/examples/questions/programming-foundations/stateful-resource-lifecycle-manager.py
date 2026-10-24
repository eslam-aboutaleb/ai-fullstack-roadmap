"""Stateful resource lifecycle encapsulation suite.

Demonstrates when a Python class is necessary versus a function and dictionary:
1. Stateless transformations: standalone pure functions operating on immutable dicts/tuples
   are superior for data pipelines, avoiding unnecessary class overhead.
2. Stateful resource lifecycle: when an entity maintains mutable state, concurrency locks,
   or external connection handles (e.g. database sessions, sockets), a class encapsulates
   invariants and implements the Context Manager protocol (__enter__ / __exit__) to guarantee cleanup.
3. Invariant protection: prevents callers from corrupting internal flags or executing operations
   on closed/exhausted resources.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ResourceClosedError(RuntimeError):
    """Raised when an operation is attempted on a closed resource."""
    pass


# 1. Stateless functional transformation: A class is NOT needed here.
def normalize_user_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Pure function: takes input, returns new transformed dictionary without side effects."""
    return {
        "user_id": str(raw.get("id", "")).strip().lower(),
        "email": str(raw.get("email", "")).strip().lower(),
        "is_active": bool(raw.get("active", False)),
    }


# 2. Stateful resource management: A class is ESSENTIAL here.
class DatabaseConnectionSession:
    """Encapsulates connection lifecycle, transaction state, and cleanup invariants."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._is_connected: bool = False
        self._in_transaction: bool = False
        self._query_log: List[str] = []

    def connect(self) -> None:
        if self._is_connected:
            return
        self._is_connected = True

    def close(self) -> None:
        if self._in_transaction:
            self._rollback()
        self._is_connected = False

    def execute_query(self, sql: str) -> str:
        if not self._is_connected:
            raise ResourceClosedError(f"Cannot execute query on closed connection to {self._dsn}")
        self._query_log.append(sql)
        return f"Result for: {sql}"

    def begin_transaction(self) -> None:
        if not self._is_connected:
            raise ResourceClosedError("Cannot begin transaction on closed connection")
        self._in_transaction = True

    def commit(self) -> None:
        self._in_transaction = False

    def _rollback(self) -> None:
        self._in_transaction = False
        self._query_log.append("ROLLBACK")

    # Context Manager implementation
    def __enter__(self) -> DatabaseConnectionSession:
        self.connect()
        self.begin_transaction()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is not None:
                self._rollback()
            else:
                self.commit()
        finally:
            self.close()


def run_test_suite() -> None:
    # 1. Test pure functional transformation (No class needed):
    raw_user = {"id": "  USR-401 ", "email": "User@Domain.COM ", "active": 1}
    normalized = normalize_user_record(raw_user)
    assert normalized == {"user_id": "usr-401", "email": "user@domain.com", "is_active": True}
    assert raw_user["email"] == "User@Domain.COM "  # Original remains unmutated

    # 2. Test stateful class lifecycle with Context Manager:
    dsn = "postgres://user:pass@localhost:5432/app"
    session_ref: Optional[DatabaseConnectionSession] = None

    with DatabaseConnectionSession(dsn) as session:
        session_ref = session
        assert session._is_connected is True
        assert session._in_transaction is True

        res = session.execute_query("SELECT * FROM documents WHERE id = 1")
        assert "SELECT * FROM documents" in res

    # On block exit, __exit__ guaranteed close:
    assert session_ref is not None
    assert session_ref._is_connected is False
    assert session_ref._in_transaction is False

    # 3. Test invariant protection: executing query after close raises ResourceClosedError:
    caught_closed = False
    try:
        session_ref.execute_query("SELECT 1")
    except ResourceClosedError as err:
        caught_closed = True
        assert "Cannot execute query on closed connection" in str(err)

    assert caught_closed is True, "Must reject queries on closed session"

    # 4. Test exception rollback safety:
    exception_caught = False
    failed_session: Optional[DatabaseConnectionSession] = None
    try:
        with DatabaseConnectionSession(dsn) as session:
            failed_session = session
            session.execute_query("UPDATE accounts SET balance = 0")
            raise ValueError("Simulated downstream business logic crash")
    except ValueError:
        exception_caught = True

    assert exception_caught is True
    assert failed_session is not None
    assert failed_session._is_connected is False
    assert "ROLLBACK" in failed_session._query_log

    print("All stateful resource lifecycle assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
