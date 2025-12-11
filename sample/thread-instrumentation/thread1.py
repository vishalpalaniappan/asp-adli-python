import threading
import queue
import time
import random

def testFunc():
    print("test func 1")
    a = 1

class Thread1(threading.Thread):
    def __init__(self, id, queue):
        super().__init__(daemon=True)
        self.id = id
        self.queue = queue
        self.start()

    def __del__(self):
        print("Closed Thread", self.id)

    def square_number(self, number):
        square = number * number
        print(f"Squared Number: {square}")


    def run(self):
        while True:
            if not self.queue.empty():
                msg = self.queue.get(timeout=0.5)
                print(f"Thread 1 Received Message: {msg}")
                self.square_number(msg["number"])
