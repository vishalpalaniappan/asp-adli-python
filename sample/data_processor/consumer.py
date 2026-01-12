import threading
import queue

class ConsumerThread(threading.Thread):
    def __init__(self, queue):
        super().__init__(daemon=True)
        self.queue = queue
        self.items = {}
        self.start()

    def run(self):
        while True:
            try:
                msg = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            self.items[msg["data"]] = self.items.get(msg["data"], 0) + 1

            if self.items[msg["data"]] == 3:
                print("Consumer received the processed data from all three workers for the following data: ", msg["data"])
                del self.items[msg["data"]]