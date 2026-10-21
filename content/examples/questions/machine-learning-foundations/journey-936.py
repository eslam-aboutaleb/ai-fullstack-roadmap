labels = [0,0,0,0,1]
predictions = [0,0,0,0,0]
accuracy = sum(a==b for a,b in zip(labels,predictions))/len(labels)
true_positive = sum(a==b==1 for a,b in zip(labels,predictions))
assert accuracy == 0.8 and true_positive == 0
print({'accuracy':accuracy,'positive_recall':0.0})

