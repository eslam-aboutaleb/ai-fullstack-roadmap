tp,fn,fp,tn=90,10,99,9801
precision=tp/(tp+fp)
recall=tp/(tp+fn)
assert tp+fn+fp+tn == 10000
assert round(precision,4)==0.4762 and recall==0.9
print(round(precision,4),recall)
