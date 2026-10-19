positions, packets = [0, 2, 4], []
for position in positions:
    blocks = ['noise'] * 4
    blocks.insert(position, 'required_fact')
    packets.append(blocks)
print([packet.index('required_fact') for packet in packets])
