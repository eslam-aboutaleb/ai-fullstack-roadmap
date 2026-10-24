release = {'offline_pass': True, 'online_latency_guardrail': False, 'online_scope_guardrail': True}
print('continue' if all(release.values()) else 'rollback')
