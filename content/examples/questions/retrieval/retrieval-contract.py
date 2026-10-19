request = {'query': 'sale', 'tenant': 'A', 'candidate_k': 20, 'final_k': 4}
valid = 0 < request['final_k'] <= request['candidate_k'] <= 100
print(valid)
