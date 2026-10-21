"""A reviewed target is not overwritten by a weak label proposal."""
current = {'label':'access','source':'human-reviewed','revision':2}
proposal = {'label':'billing','source':'teacher-model','revision':3}
accepted = current if current['source']=='human-reviewed' and proposal['source']=='teacher-model' else proposal
assert accepted is current
print('teacher proposal retained as weak evidence; reviewed target preserved')
