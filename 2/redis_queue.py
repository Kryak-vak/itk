
class RedisQueue:
    def publish(self, msg: dict):
        raise NotImplementedError

    def consume(self) -> dict:
        raise NotImplementedError


if __name__ == '__main__':
    q = RedisQueue()
    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}

