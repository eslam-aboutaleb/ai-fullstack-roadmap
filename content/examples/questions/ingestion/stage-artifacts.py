stages = ['fetch', 'extract', 'chunk', 'embed', 'publish']
complete = {'fetch', 'extract', 'chunk'}
next_stage = next(stage for stage in stages if stage not in complete)
print(next_stage, 'publish' in complete)
