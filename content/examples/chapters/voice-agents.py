class Playback:
    def __init__(self): self.generation = 1
    def interrupt(self): self.generation += 1
    def accept(self, generation, audio):
        return audio if generation == self.generation else b""
playback = Playback()
old = playback.generation
playback.interrupt()
assert playback.accept(old, b"obsolete audio") == b""
assert playback.accept(playback.generation, b"new audio") == b"new audio"
# Also stop the actual device buffer and cancel upstream work where supported.
