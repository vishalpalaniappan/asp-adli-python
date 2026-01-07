import queue
import sys
import time
import sqlite3
from consumer import ConsumerThread
from worker import WorkerThread

def ingestor():
    conn = sqlite3.connect('jobs.db')

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, item TEXT)")
    conn.commit()

    consumer_queue = queue.Queue()
    ConsumerThread(consumer_queue)

    message_queue_a = queue.Queue()
    message_queue_b = queue.Queue()
    message_queue_c = queue.Queue()

    WorkerThread(1, message_queue_a, consumer_queue)
    WorkerThread(2, message_queue_b, consumer_queue)
    WorkerThread(3, message_queue_c, consumer_queue)

    while True:
        print("\nEnter Job id:")        
        data = input("ID (ex: 1,5,4,3,9): ")
        message_queue_a.put(data)
        message_queue_b.put(data)
        message_queue_c.put(data)
        time.sleep(1)

if "__main__" == __name__:
    sys.exit(ingestor())