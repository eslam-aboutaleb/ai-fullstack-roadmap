now, last_pong, last_progress = 100, 99, 20
connection_alive = now-last_pong < 10
task_stalled = now-last_progress > 30
print(connection_alive, task_stalled)
