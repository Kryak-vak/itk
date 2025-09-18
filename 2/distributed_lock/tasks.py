import time
from datetime import timedelta

from locks import single


@single(max_processing_time=timedelta(minutes=2))
def process_transaction():
    print("process_transaction start")
    time.sleep(1)
    print("process_transaction finish after 1 sec")


@single
def process_other_transaction():
    print("process_other_transaction start")
    time.sleep(1)
    print("process_other_transaction finish after 1 sec")

