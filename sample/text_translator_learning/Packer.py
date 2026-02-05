import threading
import queue
from TransactionDB import TransactionDB

class PackerThread(threading.Thread):
    def __init__(self, queue):
        super().__init__(daemon=True)
        self.queue = queue
        self.items = {}
        self.start()

    def run(self):
        self.db = TransactionDB()
        while True:
            try:
                msg = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            self.db.addTranslation(msg)

            if self.db.isDone(msg):
                self.db.setDone(msg)