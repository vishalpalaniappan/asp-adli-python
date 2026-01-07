import queue
import sys
import time
from consumer import ConsumerThread
from worker import WorkerThread

def producer():
    consumer_queue = queue.Queue()
    ConsumerThread(consumer_queue)

    message_queue_a = queue.Queue()
    message_queue_b = queue.Queue()
    message_queue_c = queue.Queue()

    WorkerThread(1, message_queue_a, consumer_queue)
    WorkerThread(2, message_queue_b, consumer_queue)
    WorkerThread(3, message_queue_c, consumer_queue)

    while True:    
        data = input("\nEnter any string:")
        message_queue_a.put(data)
        message_queue_b.put(data)
        message_queue_c.put(data)
        time.sleep(1)

if "__main__" == __name__:
    sys.exit(producer())