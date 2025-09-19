import random
import time
from typing import cast

from redis import Redis

redis_cli = Redis(host='localhost', port=6379, decode_responses=True)


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def test(self) -> bool:
        def get_time_float() -> float:
            secs, microsecs = get_time()
            return secs + microsecs / 1_000_000
        
        def get_time() -> tuple[int, int]:
            return  cast(tuple[int, int], redis_cli.time())

        name_key = f"rate_limiter_{id(self)}"
        exp_secs = 3
        rate_limit = 5

        cur_time = get_time_float()

        redis_cli.zremrangebyscore(name_key, 0, cur_time - exp_secs)

        request_count = cast(
            int, redis_cli.zcount(name_key, cur_time - exp_secs, cur_time)
        )
        
        if request_count >= rate_limit:
            return False

        set_item = {str(cur_time): cur_time}
        redis_cli.zadd(name_key, set_item)

        return True
    

def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


def test_request(rate_limiter):
    try:
        make_api_request(rate_limiter)
    except RateLimitExceed:
        print("Rate limit exceed!")
    else:
        print("All good")


if __name__ == '__main__':
    # test 1
    print("Starting test 1")
    
    rate_limiter = RateLimiter()
    for i in range(6):
        test_request(rate_limiter)
    

    # test 2
    print("\nStarting test 2")

    rate_limiter = RateLimiter()
    for i in range(5):
        test_request(rate_limiter)
        time.sleep(1)
    time.sleep(0.1)

    for i in range(5):
        test_request(rate_limiter)
    
    
    # test 3
    print("\nStarting test 3")

    rate_limiter = RateLimiter()
    for _ in range(50):
        time.sleep(random.randint(1, 2))
        test_request(rate_limiter)

