import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool as MultiprocessingPool
from multiprocessing import Process, Queue, cpu_count
from random import randint
from time import perf_counter

import matplotlib.pyplot as plt

sys.setrecursionlimit(1100)


class Timer:
    durations = {}

    def __init__(self, name: str) -> None:
        self.name = name
    
    def __enter__(self) -> None:
        self.start = perf_counter()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        duration = perf_counter() - self.start
        Timer.durations[self.name] = duration
        

def write_time(func):
    def wrapper(*args, **kwargs):
        kwargs_s = f": {kwargs}" if kwargs else ""
        func_name = f"{func.__name__}{kwargs_s}"
        with Timer(func_name):
            result = func(*args, **kwargs)
        
        return result
    return wrapper


def generate_data(n: int) -> list[int]:
    data = []
    for _ in range(n):
        data.append(randint(1, 1000))
    
    return data


def procces_number(number: int) -> None:
    is_prime(number)


def factorial(number: int) -> int:
    if number <= 1:
        return number
    
    return number * factorial(number - 1)


def is_prime(number: int) -> bool:
    def calc_prime(number: int, divisor: int) -> bool:
        remainder = number % divisor
        if not remainder:
            return False
        else:
            if divisor < number // 2:
                return calc_prime(number, divisor + 1)
        
        return True
    
    if number <= 2:
        return True
    
    divisor_start = 2

    return calc_prime(number, divisor_start)


# 0) Main thread only
@write_time
def main_thread(numbers: list[int]) -> None:
    for num in numbers:
        procces_number(num)


# 1) Thread pool
@write_time
def thread_pool(numbers: list[int]) -> None:
    # cpu_count here only for comparison with mp
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        executor.map(procces_number, numbers)


# 2) Multiprocessing pool
@write_time
def multi_pool(numbers: list[int]) -> None:
    with MultiprocessingPool(cpu_count()) as pool:
        pool.map(procces_number, numbers)


# 3) Multiprocessing Process and Queue
@write_time
def multi_process_queue(numbers: list[int], chunk_size: int = 1) -> None:
    queue = Queue()
    consumer_count = cpu_count() - 1
    producer_proc = Process(
        target=producer,
        args=(queue, consumer_count, chunk_size, numbers)
    )

    consumer_procs = []
    for _ in range(consumer_count):
        consumer_procs.append(
            Process(target=consumer, args=(queue, ))
        )
    
    for proc in (producer_proc, *consumer_procs):
        proc.start()
    
    for proc in (producer_proc, *consumer_procs):
        proc.join()


def producer(
        queue: Queue, consumer_count: int, chunk_size: int,
        numbers: list[int]
    ) -> None:
    for i in range(0, len(numbers), chunk_size):
        queue.put(numbers[i:i+chunk_size])

    for _ in range(consumer_count):
        queue.put(None)


def consumer(queue: Queue) -> None:
    while True:
        chunk = queue.get()
        if chunk is None:
            break
        
        for num in chunk:
            procces_number(num)


def visualize(durations: dict):
    names = list(durations.keys())
    values = list(durations.values())

    plt.figure(figsize=(12, 6))
    bars = plt.bar(names, values)
    
    plt.xticks(rotation=30, ha="right")
    
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{val:.2f}", ha="center", va="bottom")

    plt.ylabel("Execution time (s)")
    plt.title("Durations:")

    plt.tight_layout()
    plt.savefig("./data/threads_processes/durations.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    numbers = generate_data(1000000)

    main_thread(numbers)
    thread_pool(numbers)
    multi_pool(numbers)
    multi_process_queue(numbers)
    multi_process_queue(numbers, chunk_size=1000)
    multi_process_queue(numbers, chunk_size=10000)
    multi_process_queue(numbers, chunk_size=100000)

    visualize(Timer.durations)
