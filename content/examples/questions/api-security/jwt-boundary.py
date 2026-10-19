checks = {'signature_verified': True, 'issuer_matches': True,
          'audience_matches': False, 'not_expired': True}
accepted = all(checks.values())
print(accepted)
