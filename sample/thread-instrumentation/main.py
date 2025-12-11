import queue
import time
import sys
import random
import threading
from thread1 import Thread1

def main(argv):
    print("MAIN THREAD:", threading.get_ident())
    message_queue = queue.Queue()

    Thread1(1, message_queue)

    print("Main: Threads started and running in background.\n")

    # Check for messages until timeout or keyboard interrupt
    while True:
        job = {"number":random.randint(1, 10)}
        print(f"\nMain thread, number to square {job}")
        message_queue.put(job)
        time.sleep(1)

if "__main__" == __name__:
    sys.exit(main(sys.argv))