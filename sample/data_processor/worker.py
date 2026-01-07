import threading
import queue

class WorkerThread(threading.Thread):
    def __init__(self, id, queue, consumerQueue):
        super().__init__(daemon=True)
        self.book_shelf = {}
        self.queue = queue
        self.id = id
        self.consumer_queue = consumerQueue
        self.start()

    def __del__(self):
        print(f"{threading.get_ident()} Terminating worker thread.")

    def run(self):
        while True:
            try:
                msg = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            print("Worker Received message:", msg)
            self.consumer_queue.put({
                "id": self.id,
                "data": msg
            })