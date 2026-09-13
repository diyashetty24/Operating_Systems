import threading
import time
import random
from collections import deque

class SharedBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = deque()
        self.condition = threading.Condition()

    def produce(self, item):
        with self.condition:
        
            while len(self.items) >= self.capacity:
                print(f"Buffer is full, producer is waiting(size={len(self.items)})")
                self.condition.wait()

            self.items.append(item)
            print(f"Produced -> {item} | buffer size: {len(self.items)}")

            self.condition.notify_all()

    def consume(self):
        with self.condition:
            while len(self.items) == 0:
                print(f"Buffer is empty, consumer is waiting (size={len(self.items)})")
                self.condition.wait()

            item = self.items.popleft()
            print(f"Consumed -> {item} | buffer size: {len(self.items)}")

            self.condition.notify_all()
            return item


def producer_job(buffer, item_count, name="Producer"):
    for i in range(1, item_count + 1):
        buffer.produce(i)
        time.sleep(random.uniform(0.05, 0.2))
    print(f"{name} finished producing {item_count} items.")

def consumer_job(buffer, item_count, name="Consumer"):
    for _ in range(item_count):
        buffer.consume()
        time.sleep(random.uniform(0.1, 0.3))
    print(f"{name} finished consuming {item_count} items.")


def main():
    buffer_capacity = 5
    total_items = 10

    shared_buffer = SharedBuffer(buffer_capacity)

    producer_thread = threading.Thread(
        target=producer_job, args=(shared_buffer, total_items), name="Producer-Thread"
    )
    consumer_thread = threading.Thread(
        target=consumer_job, args=(shared_buffer, total_items), name="Consumer-Thread"
    )

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()

    print("Both producer and consumer have finished Program exiting.")

if __name__ == "__main__":
    main()
