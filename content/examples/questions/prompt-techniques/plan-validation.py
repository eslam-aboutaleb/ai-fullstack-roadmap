plan = ['search_policy', 'export_all']
allowed = {'search_policy', 'get_order'}
valid = all(step in allowed for step in plan)
print(valid)
