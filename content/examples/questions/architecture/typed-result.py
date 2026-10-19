from dataclasses import dataclass
@dataclass
class Result:
    status: str
    task_id: str
    diagnostic: str = ''
result = Result('not_found', 'T1', 'internal lookup detail')
public = {'status': result.status, 'task_id': result.task_id}
print(public)
