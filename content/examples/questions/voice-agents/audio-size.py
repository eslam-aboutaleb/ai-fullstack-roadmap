sample_rate, channels, bits = 16000, 1, 16
bytes_per_second = sample_rate*channels*bits//8
frame_bytes = bytes_per_second*20//1000
print(bytes_per_second, frame_bytes)
