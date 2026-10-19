contract = {'events': {'method': 'GET', 'path': '/tasks/T1/events'},
            'cancel': {'method': 'POST', 'path': '/tasks/T1/cancel'}}
print(contract['events']['method'], contract['cancel']['method'])
