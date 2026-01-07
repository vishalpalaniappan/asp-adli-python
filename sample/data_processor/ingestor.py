import queue
import sys
from worker import WorkerThread

def ingestor():
    message_queue = queue.Queue()

    WorkerThread(message_queue)

    while True:
        print("\nEnter Job id:")        
        data = input("ID (ex: 1,5,4,3,9): ")
        message_queue.put(data)

if "__main__" == __name__:
    sys.exit(ingestor())