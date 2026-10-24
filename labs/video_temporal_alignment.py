"""Timebase-correct audio/video alignment and owner-scoped clip retrieval.

PTS are integer ticks with rational seconds-per-tick. No video codec,
learned multimodal model, STT engine or multimedia network access is used.
"""
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class Frame:
    pts: int
    time_base: Fraction
    owner: str
    asset: str
    label: str

    def seconds(self):
        if self.pts<0 or self.time_base<=0:raise ValueError("bad frame timestamp")
        return self.pts*self.time_base

@dataclass(frozen=True)
class Transcript:
    start: Fraction
    end: Fraction
    owner: str
    asset: str
    words: str

def uniform_sample(frames, *, every_seconds, owner):
    if every_seconds<=0:raise ValueError("positive sampling interval required")
    selected=[];next_time=Fraction(0)
    for frame in sorted((x for x in frames if x.owner==owner),key=lambda x:x.seconds()):
        if frame.seconds()>=next_time:
            selected.append(frame)
            next_time=frame.seconds()+every_seconds
    return selected

def overlap(a,b,c,d):
    if a>b or c>d:raise ValueError("reversed interval")
    return max(Fraction(0),min(b,d)-max(a,c))

def align(frames, transcript, *, owner):
    if transcript.owner!=owner:return []
    if transcript.start<0 or transcript.start>=transcript.end:
        raise ValueError("invalid transcript interval")
    return [f for f in frames if f.owner==owner and f.asset==transcript.asset
            and transcript.start<=f.seconds()<transcript.end]

def estimate_drift(*, audio_anchor_start, video_anchor_start,
                   audio_anchor_end, video_anchor_end, max_abs_seconds):
    if max_abs_seconds<0:raise ValueError("invalid sync tolerance")
    start=audio_anchor_start-video_anchor_start
    end=audio_anchor_end-video_anchor_end
    return {"start_offset":start,"end_offset":end,"drift":end-start,
            "within_tolerance":abs(start)<=max_abs_seconds and abs(end)<=max_abs_seconds}

def cite_clips(frames,transcripts,*,owner,phrase):
    evidence=[]
    for segment in transcripts:
        if segment.owner!=owner or phrase.casefold() not in segment.words.casefold():
            continue
        visible=align(frames,segment,owner=owner)
        if visible:
            evidence.append({"asset":segment.asset,
                             "start":str(segment.start),"end":str(segment.end),
                             "frame_pts":[x.pts for x in visible],
                             "source":"synthetic-transcript-clip"})
    return evidence

def check():
    tick=Fraction(1,90000)
    a=[Frame(i*90000,tick,"A","clip1",f"frame{i}") for i in [0,1,2,3]]
    b=[Frame(i*90000,tick,"B","private",f"private{i}") for i in [0,1,2]]
    # Keep presentation timestamps rather than assuming presentation at decode order.
    assert [x.pts for x in uniform_sample(a+b,every_seconds=Fraction(2),owner="A")]==[0,180000]
    words=[Transcript(Fraction(1),Fraction(3),"A","clip1","Driver opens door"),
           Transcript(Fraction(0),Fraction(3),"B","private","Driver opens door")]
    assert [f.label for f in align(a,words[0],owner="A")]==["frame1","frame2"]
    result=cite_clips(a+b,words,owner="A",phrase="opens")
    assert len(result)==1 and result[0]["asset"]=="clip1"
    assert cite_clips(a+b,words,owner="C",phrase="opens")==[]
    assert overlap(Fraction(0),Fraction(4),Fraction(2),Fraction(6))==2
    drift=estimate_drift(audio_anchor_start=Fraction(1,20),video_anchor_start=0,
                         audio_anchor_end=Fraction(11,1),video_anchor_end=10,
                         max_abs_seconds=Fraction(1,10))
    assert drift["within_tolerance"] is False and drift["drift"]==Fraction(19,20)
    for fn in [lambda:uniform_sample(a,every_seconds=Fraction(0),owner="A"),
               lambda:align(a,Transcript(3,2,"A","clip1","x"),owner="A"),
               lambda:overlap(3,1,0,5)]:
        try:fn()
        except ValueError:pass
        else:raise AssertionError("invalid temporal input accepted")
    print("Video timebase: PTS sampling, transcript alignment, drift, owner-scoped citations PASS")
if __name__=="__main__":check()
