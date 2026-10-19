function showCompletedAnswer(task) {
  const answer = document.querySelector('#answer');
  const status = document.querySelector('#status');
  answer.textContent = task.answer;
  status.setAttribute('role', 'status');
  status.textContent = 'Answer ready';
}
