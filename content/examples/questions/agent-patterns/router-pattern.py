routes = {'status': lambda: 'order_status', 'policy': lambda: 'policy_search'}
intent = 'status'
print(routes[intent]())
