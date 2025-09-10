import time
from datetime import datetime


class Meta(type):
    created_at = None

    def __new__(cls, name, bases, attrs):
        attrs["created_at"] = datetime.today()
        return super().__new__(cls, name, bases, attrs)


class Foo(metaclass=Meta):
    pass

time.sleep(1)

class Bar(metaclass=Meta):
    pass


if __name__ == "__main__":
    print(Foo.created_at)
    print(Bar.created_at)
