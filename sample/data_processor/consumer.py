import threading
import queue

class ConsumerThread(threading.Thread):
    def __init__(self, queue):
        super().__init__(daemon=True)
        self.book_shelf = {}
        self.queue = queue
        self.start()

    def __del__(self):
        print(f"{threading.get_ident()} Terminating consumer thread")

    def run(self):
        while True:
            try:
                msg = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            print("Consumer Received message:", msg)