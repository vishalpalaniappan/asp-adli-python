import threading
import queue

class PackerThread(threading.Thread):
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

            self.items[msg["original"]] = self.items.get(msg["original"], 0) + 1

            if self.items[msg["original"]] == 3:
                del self.items[msg["original"]]