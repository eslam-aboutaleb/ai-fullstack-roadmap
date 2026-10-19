from contextvars import ContextVar
principal = ContextVar('principal', default=None)
token = principal.set('A')
try:
    print(principal.get(), end=' ')
finally:
    principal.reset(token)
print(principal.get())
