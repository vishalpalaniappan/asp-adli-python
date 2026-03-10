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
                translatedJobPart = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            self.db.addTranslation(translatedJobPart)

            if self.db.isDone(translatedJobPart["uid"]):
                self.db.setDone(translatedJobPart["uid"])