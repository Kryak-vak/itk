import unittest.mock


class CacheMock:
    cached_data = {}

    @classmethod
    def get(cls, func_id, args_key):
        if func_id not in cls.cached_data:
            return None

        return cls.cached_data[func_id].get(args_key)

    @classmethod
    def set(cls, func_id: str, args_key, value) -> None:
        if func_id not in cls.cached_data:
            cls.cached_data[func_id] = {}

        cls.cached_data[func_id][args_key] = value
    
    @classmethod
    def get_size(cls, func_id: str) -> int:
        return len(cls.cached_data.get(func_id, []))


def lru_cache(maxsize: int = 4):
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = getattr(func, "__name__", str(func))
            args_key = (*args, *kwargs)

            res = CacheMock.get(func_name, args_key)

            if res is None:
                res = func(*args, **kwargs)
            
            size = CacheMock.get_size(func_name)
            if maxsize >= size:
                CacheMock.set(func_name, args_key, res)

            return res

        return wrapper
    return decorator


@lru_cache()
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache()
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == '__main__':
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
