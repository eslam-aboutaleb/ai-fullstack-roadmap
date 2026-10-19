trace = ['read_order', 'read_policy', 'review', 'write']
position = {step: index for index, step in enumerate(trace)}
valid = all(position[step] < position['review'] < position['write']
            for step in ('read_order', 'read_policy'))
print(valid)
