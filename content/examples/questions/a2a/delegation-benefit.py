requirements = {'remote_owned_capability': False, 'independent_delivery_needed': False}
choice = 'delegate' if any(requirements.values()) else 'local_service'
print(choice)
