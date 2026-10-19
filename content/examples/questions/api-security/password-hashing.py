from argon2 import PasswordHasher
hasher = PasswordHasher()
stored_hash = hasher.hash('synthetic-example-password')
verified = hasher.verify(stored_hash, 'synthetic-example-password')
if hasher.check_needs_rehash(stored_hash):
    stored_hash = hasher.hash('synthetic-example-password')
print(verified)
