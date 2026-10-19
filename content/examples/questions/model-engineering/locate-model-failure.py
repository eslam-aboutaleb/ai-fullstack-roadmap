stages = {'retrieved_required_evidence': False, 'context_correct': False, 'answer_correct': False}
next_work = 'retrieval' if not stages['retrieved_required_evidence'] else 'model_behavior'
print(next_work)
