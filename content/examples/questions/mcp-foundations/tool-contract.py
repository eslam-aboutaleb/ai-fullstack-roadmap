arguments = {'document_id': 'D1', 'max_chars': 1000000}
valid = (set(arguments) == {'document_id', 'max_chars'}
         and isinstance(arguments['document_id'], str)
         and type(arguments['max_chars']) is int
         and 0 < arguments['max_chars'] <= 2000)
print(valid)
