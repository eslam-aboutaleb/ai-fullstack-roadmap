request_bytes, user_inflight, tool_calls = 1200, 2, 6
admitted = request_bytes <= 4096 and user_inflight < 4 and tool_calls < 5
print(admitted)
