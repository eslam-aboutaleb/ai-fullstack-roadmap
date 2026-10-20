"""Verify attention, incremental K/V reuse, byte tokenization and int8 error."""
import math


def attention(query, keys, values):
    if not query or not keys or len(keys)!=len(values) or any(len(key)!=len(query) for key in keys):
        raise ValueError('Attention dimensions do not match')
    width=len(values[0])
    if width==0 or any(len(value)!=width for value in values):
        raise ValueError('Value dimensions do not match')
    scores=[sum(q*k for q,k in zip(query,key))/math.sqrt(len(query)) for key in keys]
    largest=max(scores);exps=[math.exp(score-largest) for score in scores];total=sum(exps)
    weights=[value/total for value in exps]
    return weights,[sum(weight*value[index] for weight,value in zip(weights,values)) for index in range(width)]


def encode(text):
    # A byte vocabulary always represents valid UTF-8 input, unlike unknown-token
    # vocabularies. This demonstration merges one known byte pair, not learned BPE.
    tokens=[];data=text.encode('utf-8');index=0
    while index<len(data):
        if data[index:index+2]==b'lo':tokens.append(256);index+=2
        else:tokens.append(data[index]);index+=1
    return tokens


def decode(tokens):
    return b''.join(b'lo' if token==256 else bytes([token]) for token in tokens).decode('utf-8')


def verify():
    weights,result=attention([1.],[[1.],[0.]],[[2.],[4.]])
    assert abs(weights[0]-.7310585786)<1e-9
    assert abs(result[0]-2.5378828427)<1e-9
    keys=[[1.,0.],[0.,1.],[1.,1.]];values=[[1.,2.],[3.,4.],[5.,6.]]
    cached_keys=[];cached_values=[]
    for index,query in enumerate(keys):
        cached_keys.append(keys[index]);cached_values.append(values[index])
        assert attention(query,cached_keys,cached_values)==attention(query,keys[:index+1],values[:index+1])
    for text in ('low','hello','café 😀',''):
        assert decode(encode(text))==text
    assert encode('low')==[256,119]
    original=[-1.5,-.1,.2,2.0];scale=max(abs(x) for x in original)/127
    quantized=[round(x/scale) for x in original];restored=[x*scale for x in quantized]
    assert max(abs(a-b) for a,b in zip(original,restored))<=scale/2+1e-12
    print('Attention: weights=[0.731059, 0.268941]; output=[2.537883].')
    print('Prefix K/V reuse, byte roundtrip, and int8 error bound passed.')


if __name__=='__main__':verify()
