"""Demonstrate exponential backoff with full jitter for database transient errors (serialization/deadlock)."""
import random
import time

class DatabaseTransientError(Exception):
    """Corresponds to PostgreSQL SQLSTATE 40001 (serialization_failure) or 40P01 (deadlock_detected)."""
    pass

class DatabasePermanentError(Exception):
    """Corresponds to SQLSTATE 23505 (unique_violation) or foreign key constraint violations."""
    pass

def execute_with_bounded_retry(operation, max_attempts=4, base_backoff=0.01, max_backoff=0.2):
    attempts = 0
    while True:
        attempts += 1
        try:
            return operation(attempts), attempts
        except DatabaseTransientError as e:
            if attempts >= max_attempts:
                raise RuntimeError(f"Exhausted {max_attempts} retry attempts on transient DB error: {e}")
            
            # Full Jitter Exponential Backoff formula: sleep = uniform(0, min(max_backoff, base * 2^attempt))
            calculated_backoff = min(max_backoff, base_backoff * (2 ** (attempts - 1)))
            sleep_duration = random.uniform(0, calculated_backoff)
            time.sleep(sleep_duration)
        except DatabasePermanentError:
            # Permanent errors (e.g. unique constraint violation) MUST NOT be retried:
            raise

# Simulate a transient serialization failure that clears on the 3rd attempt
def mock_transactional_operation(attempt):
    if attempt < 3:
        raise DatabaseTransientError("PostgreSQL 40001: could not serialize access due to concurrent update")
    return "TRANSACTION_COMMITTED"

result, total_attempts = execute_with_bounded_retry(mock_transactional_operation)
assert result == "TRANSACTION_COMMITTED"
assert total_attempts == 3

# Verify that permanent errors fail fast without retry
permanent_failed_immediately = False
def failing_operation(attempt):
    raise DatabasePermanentError("PostgreSQL 23505: duplicate key value violates unique constraint")

try:
    execute_with_bounded_retry(failing_operation)
except DatabasePermanentError:
    permanent_failed_immediately = True

assert permanent_failed_immediately is True
print(f"Retry policy verified: transient_succeeded={result} in {total_attempts} attempts; permanent_fail_fast={permanent_failed_immediately}")
