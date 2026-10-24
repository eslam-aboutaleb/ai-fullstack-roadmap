"""Offline worked calculations for the additional foundation lessons.

Run with Python 3.10+: python examples/labs/foundation_bridge.py
Only synthetic fixtures and the Python standard library are used.
Change a fixture, predict the outcome, then run it again.
This is a calculation and SQL exercise, not a trained AI application.
"""
import math
import sqlite3


def cosine(left: list[float], right: list[float]) -> float:
    """Compare equally sized nonzero vectors; reject undefined comparisons."""
    if not left or len(left) != len(right):
        raise ValueError('Vectors must have the same nonzero dimension')
    if not all(math.isfinite(x) for x in left + right):
        raise ValueError('Coordinates must be finite')
    denominator = math.sqrt(sum(x*x for x in left) * sum(x*x for x in right))
    if denominator == 0:
        raise ValueError('Cosine is undefined for a zero vector')
    return sum(x*y for x, y in zip(left, right)) / denominator


def ranked_metrics(ranked: list[str], relevant: set[str]) -> dict[str, float]:
    """Use unique document IDs and a nonempty labeled relevant set."""
    if not relevant or not ranked or len(ranked) != len(set(ranked)):
        raise ValueError('Use nonempty labels and a unique nonempty ranking')
    hits = [position for position, item in enumerate(ranked, 1) if item in relevant]
    return {
        'precision': len(hits) / len(ranked),
        'recall': len(hits) / len(relevant),
        'reciprocal_rank': 1 / hits[0] if hits else 0.0,
    }


def gradient_step(weight: float, learning_rate: float) -> tuple[float, float]:
    """One update for squared error on the synthetic example x=2, y=6."""
    gradient = 2 * 2 * (weight * 2 - 6)
    new_weight = weight - learning_rate * gradient
    return new_weight, (new_weight * 2 - 6) ** 2


def sql_fixture() -> list[tuple]:
    """Demonstrate keys, a join, and parameter binding in an in-memory database.

    SQLite makes this fixture runnable offline. It does not demonstrate
    PostgreSQL roles, row security, or production concurrency semantics.
    """
    connection = sqlite3.connect(':memory:')
    try:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.executescript('''
            CREATE TABLE documents (id TEXT PRIMARY KEY, owner_id TEXT NOT NULL);
            CREATE TABLE revisions (
                document_id TEXT REFERENCES documents(id),
                revision INTEGER NOT NULL,
                text TEXT NOT NULL,
                UNIQUE(document_id, revision)
            );
        ''')
        connection.execute('INSERT INTO documents VALUES (?, ?)', ('D1', 'user-a'))
        connection.execute('INSERT INTO revisions VALUES (?, ?, ?)',
                           ('D1', 2, 'Sale items allow exchange only.'))
        query = '''SELECT r.document_id, r.revision, r.text
                   FROM revisions r JOIN documents d ON d.id=r.document_id
                   WHERE d.owner_id=?'''
        assert connection.execute(query, ('user-b',)).fetchall() == []
        # A hostile-looking value remains data because it is bound, not interpolated.
        assert connection.execute(query, ("user-a' OR 1=1 --",)).fetchall() == []
        return connection.execute(query, ('user-a',)).fetchall()
    finally:
        connection.close()


def main() -> None:
    weight, loss = gradient_step(1, 0.1)
    assert math.isclose(weight, 2.6) and math.isclose(loss, 0.64)
    assert gradient_step(1, 1)[1] > 16  # A large learning rate worsens the loss.
    score = cosine([1, 0], [1, 1])
    assert math.isclose(score, 1 / math.sqrt(2))
    metrics = ranked_metrics(['B', 'A', 'D'], {'A', 'C'})
    assert metrics == {'precision': 1/3, 'recall': 1/2, 'reciprocal_rank': 1/2}
    for left, right in [([0, 0], [1, 1]), ([1], [1, 2])]:
        try:
            cosine(left, right)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid vector comparison was accepted')
    print('Gradient:', {'weight': weight, 'loss': round(loss, 6)})
    print('Cosine:', round(score, 6))
    print('Retrieval:', metrics)
    print('Authorized SQL result:', sql_fixture())
    print('Next: change learning rate, ranking, and owner; predict each result.')


if __name__ == '__main__':
    main()
