from pathlib import Path
root = Path('/tmp/learning-fixture').resolve()
candidate = (root / '../outside.txt').resolve()
print(candidate.is_relative_to(root))
