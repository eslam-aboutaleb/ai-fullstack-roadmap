def choose(media=False, duplex=False):
    return 'webrtc' if media else ('websocket' if duplex else 'sse')
print(choose(media=True), choose(duplex=True), choose())
