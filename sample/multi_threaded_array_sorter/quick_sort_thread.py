import threading
import queue

class QuickSortThread(threading.Thread):
    def __init__(self, queue):
        super().__init__(daemon=True)
        self.book_shelf = {}
        self.queue = queue
        self.start()

    def __del__(self):
        print(f"{threading.get_ident()} Terminating book shelf thread")

    def run(self):
        '''
        Runs the bookshelf thread, waiting for messages from the
        main thread via the message queue. Performs operations
        based on the message type.
        
        :param self: The object itself.
        '''
        while True:
            try:
                msg = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            print("Quicksort Received message:", msg)