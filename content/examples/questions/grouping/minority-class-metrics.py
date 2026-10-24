"""A majority classifier can be accurate while missing every positive."""
truth = [0]*99 + [1]
prediction = [0]*100
accuracy = sum(a==b for a,b in zip(truth,prediction))/len(truth)
positive_recall = sum(a==1 and b==1 for a,b in zip(truth,prediction))/sum(a==1 for a in truth)
assert accuracy == 0.99 and positive_recall == 0
print('accuracy: 0.99; minority recall: 0.0')
