def answer(question: str) -> str:
    if not question.strip():
        raise ValueError('question is required')
    return 'ready'

if __name__ == '__main__':
    print('Run with Python 3.10+:', answer('policy?'))
