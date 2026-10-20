"""Optional local FastAPI lab. Install fastapi and httpx; run this file to test.

No authentication or persistent task queue: this teaches validation only.
"""
from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

    @field_validator('question')
    @classmethod
    def reject_blank(cls, value):
        if not value.strip():
            raise ValueError('question must not be blank')
        return value


@app.post('/questions', status_code=202)
def ask(question: Question):
    # Demonstration response only: no job is persisted or actually scheduled.
    return {'task_id': str(uuid4()), 'status': 'demo-accepted'}


if __name__ == '__main__':
    from fastapi.testclient import TestClient
    client = TestClient(app)
    valid = client.post('/questions', json={'question': 'Can I return this?'})
    assert valid.status_code == 202
    assert valid.json()['status'] == 'demo-accepted'
    for payload in ({}, {'question': ''}, {'question': '   '}, {'question': 'x' * 1001}, {'question': 12}):
        assert client.post('/questions', json=payload).status_code == 422
    assert client.post('/questions', content='{bad', headers={'content-type': 'application/json'}).status_code == 422
    print('Valid request: 202. Missing, blank, oversized, wrong-type, and malformed input: 422.')
