import codecs

def parse_sse(chunks):
    decoder = codecs.getincrementaldecoder("utf-8-sig")()
    line, data, kind, last_id, skip_lf, events = "", [], "", "", False, []
    def consume_line(value):
        nonlocal data, kind, last_id
        if value == "":
            if data:
                events.append({"event": kind or "message", "id": last_id,
                               "data": "\n".join(data)})
            data, kind = [], ""
            return
        if value.startswith(":"): return
        field, sep, text = value.partition(":")
        if text.startswith(" "): text = text[1:]
        if field == "data":
            data.append(text)
            if sum(map(len, data)) > 1_000_000: raise ValueError("event too large")
        elif field == "event": kind = text
        elif field == "id" and "\x00" not in text: last_id = text
        # retry and unknown fields are intentionally not acted on by this decoder.
    for chunk in chunks:
        for char in decoder.decode(chunk):
            if skip_lf:
                skip_lf = False
                if char == "\n": continue
            if char in "\r\n":
                consume_line(line)
                line = ""
                skip_lf = char == "\r"
            else:
                line += char
                if len(line) > 65536: raise ValueError("line too large")
    decoder.decode(b"", final=True)  # Reject truncated UTF-8; do not dispatch partial events.
    return events

raw = "id: 1\r\nevent: delta\r\ndata: Héllo\r\ndata: world\r\n\r\n".encode()
for split in range(len(raw) + 1):
    assert parse_sse([raw[:split], raw[split:]])[0]["data"] == "Héllo\nworld"
