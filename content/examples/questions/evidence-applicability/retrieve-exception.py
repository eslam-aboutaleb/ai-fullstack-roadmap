rule = {'returns_allowed': True, 'excludes_final_sale': True}
item = {'final_sale': True}
eligible = rule['returns_allowed'] and not (rule['excludes_final_sale'] and item['final_sale'])
print(eligible)
