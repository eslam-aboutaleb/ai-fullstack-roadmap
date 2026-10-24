stages_ms = {'queue': 100, 'retrieve': 150, 'model': 600, 'render_or_audio': 250}
total_ms = sum(stages_ms.values())
print(total_ms, total_ms <= 1000)
