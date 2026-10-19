intent = {'asr_confidence': 0.99, 'principal_verified': True,
          'exact_parameters_confirmed': False, 'revision_current': True}
print(intent['principal_verified'] and intent['exact_parameters_confirmed'] and intent['revision_current'])
