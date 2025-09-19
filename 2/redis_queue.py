import json
from datetime import timedelta
from typing import cast
from uuid import uuid4

from redis import Redis


class RedisQueue:
    def __init__(
            self, redis_cli: Redis,
            name: str | None = None, exp_time: timedelta | None = None
        ) -> None:
        self.redis_cli = redis_cli
        self.name_key = name or f"queue:{uuid4()}"
        
        if name is None and exp_time is None:
            self.exp_time = timedelta(minutes=5)
        else:
            self.exp_time = exp_time
        
        if self.exp_time:
            self.redis_cli.expire(self.name_key, self.exp_time)

    def publish(self, msg: dict):
        msg_str = json.dumps(msg)
        self.redis_cli.rpush(self.name_key, msg_str)

    def consume(self) -> dict | None:
        msg_str = cast(str, self.redis_cli.lpop(self.name_key))

        if msg_str:
            return json.loads(msg_str)
        
        return None


if __name__ == '__main__':
    redis_cli = Redis(host='localhost', port=6379, decode_responses=True)

    q = RedisQueue(redis_cli)
    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}

