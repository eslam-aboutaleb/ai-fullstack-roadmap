async function openTaskStream(taskId, token, signal) {
  const response = await fetch(`/tasks/${encodeURIComponent(taskId)}/events`, {
    headers: {Authorization: `Bearer ${token}`}, signal
  });
  if (!response.ok || !response.body) throw new Error('Stream unavailable');
  return response.body;
}
