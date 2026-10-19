async function createTask(question, signal) {
  const response = await fetch('/tasks', {
    method: 'POST', signal,
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question})
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const task = await response.json();
  if (typeof task.task_id !== 'string') throw new Error('Invalid task');
  return task;
}
