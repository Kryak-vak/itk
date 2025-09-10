

from typing import Any

# Meta

class MetaSingleton(type):
    _instance = None
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self._instance:
            self._instance = super().__call__(*args, **kwargs)
        
        return self._instance


class MetaSingleton1(metaclass=MetaSingleton):
    def __init__(self, value) -> None:
        self.value = value


inst1 = MetaSingleton1(1)
print(inst1)
print(MetaSingleton1._instance)
inst2 = MetaSingleton1(2)
print(inst2)
print(MetaSingleton1._instance)
print(inst1 is inst2)

print()



# __new__

class NewSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        
        return cls._instance
    
    def __init__(self, value) -> None:
        self.value = value


if __name__ == "__main__":
    inst1 = NewSingleton(1)
    print(inst1)
    print(NewSingleton._instance)
    inst2 = NewSingleton(2)
    print(inst2)
    print(NewSingleton._instance)
    print(inst1 is inst2)

    print()


    # import

    class ImportSingleton:
        pass

    singleton = ImportSingleton()

