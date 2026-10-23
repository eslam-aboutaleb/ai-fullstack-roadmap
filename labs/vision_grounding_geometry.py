"""Deterministic computer-vision geometry, grounding and mask-editing lab.

No pretrained model, image generation provider, downloaded image or GPU.
Boxes are (x_min, y_min, x_max, y_max) in the original image coordinate frame.
"""
from dataclasses import dataclass
from math import isclose

@dataclass(frozen=True)
class Box:
    x1: float
    y1: float
    x2: float
    y2: float
    def area(self):
        if self.x2<=self.x1 or self.y2<=self.y1:raise ValueError("empty/inverted box")
        return (self.x2-self.x1)*(self.y2-self.y1)

@dataclass(frozen=True)
class Detection:
    box: Box
    confidence: float
    label: str
    source: str

def iou(a,b):
    aa=a.area(); bb=b.area()
    overlap=(max(0,min(a.x2,b.x2)-max(a.x1,b.x1))*
             max(0,min(a.y2,b.y2)-max(a.y1,b.y1)))
    return overlap/(aa+bb-overlap)

def nms(detections, *, threshold):
    if not 0<=threshold<=1:raise ValueError("invalid suppression threshold")
    for d in detections:
        d.box.area()
        if not 0<=d.confidence<=1:raise ValueError("confidence out of range")
    # Score ordered, per-class suppression, stable ties, preserve citation provenance.
    ordered=sorted(detections,key=lambda d:(-d.confidence,d.label,d.source))
    kept=[]
    for d in ordered:
        if all(d.label!=x.label or iou(d.box,x.box)<=threshold for x in kept):
            kept.append(d)
    return kept

def match_grounding(predictions,truth,*, threshold=.5):
    if not 0<threshold<=1:raise ValueError("bad grounding threshold")
    for d in predictions+truth:d.box.area()
    matched=set();true_positive=0;false_positive=0
    for p in sorted(predictions,key=lambda d:-d.confidence):
        candidates=[(iou(p.box,g.box),idx) for idx,g in enumerate(truth)
                    if idx not in matched and p.label==g.label]
        if candidates and max(candidates)[0]>=threshold:
            score,index=max(candidates); matched.add(index);true_positive+=1
        else:false_positive+=1
    return {"tp":true_positive,"fp":false_positive,"fn":len(truth)-len(matched)}

def mask_edit(original,replacement,mask):
    if not original or not all(original) or len(replacement)!=len(original) or len(mask)!=len(original):
        raise ValueError("image rows must align")
    width=len(original[0])
    if any(len(row)!=width for group in (original,replacement,mask) for row in group):
        raise ValueError("unequal rows")
    if any(v not in (0,1) or type(v) is not int for row in mask for v in row):
        raise ValueError("mask must be binary")
    return [[replacement[y][x] if mask[y][x] else original[y][x]
             for x in range(width)] for y in range(len(original))]

def check():
    a=Box(0,0,10,10);b=Box(5,5,15,15)
    assert isclose(iou(a,b),25/175)
    assert iou(a,Box(20,20,30,30))==0
    detections=[
        Detection(a,.9,"invoice-total","page1:bbox1"),
        Detection(Box(1,1,11,11),.8,"invoice-total","page1:bbox2"),
        Detection(a,.75,"checkbox","page1:bbox3")]
    retained=nms(detections,threshold=.5)
    assert len(retained)==2 and {x.label for x in retained}=={"invoice-total","checkbox"}
    score=match_grounding(retained,[Detection(a,1,"invoice-total","gold"),
                                   Detection(a,1,"checkbox","gold")])
    assert score=={"tp":2,"fp":0,"fn":0}
    assert match_grounding([detections[0],detections[0]],[detections[0]])=={"tp":1,"fp":1,"fn":0}
    assert mask_edit([[1,2],[3,4]],[[9,9],[9,9]],[[0,1],[1,0]])==[[1,9],[9,4]]
    for fn in [lambda:iou(Box(0,0,0,1),a),
               lambda:nms(detections,threshold=1.2),
               lambda:nms([Detection(a,1.1,"invoice-total","page1")],threshold=.5),
               lambda:mask_edit([[1,2]],[[1]],[[1,1]])]:
        try:fn()
        except ValueError:pass
        else:raise AssertionError("bad vision geometry was accepted")
    print("Vision: exact IoU, per-class NMS, one-to-one grounding and binary masked edit PASS")
if __name__=="__main__":check()
