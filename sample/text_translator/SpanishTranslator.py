import threading
import queue
from deep_translator import GoogleTranslator

class SpanishTranslator(threading.Thread):
    def __init__(self, id, queue, consumerQueue):
        super().__init__(daemon=True)
        self.queue = queue
        self.id = id
        self.consumer_queue = consumerQueue
        self.start()

    def run(self):
        while True:
            try:
                msg = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            print("Worker Received message:", msg)
            translatedMsg = GoogleTranslator(source="auto", target="spanish").translate(msg)
            self.consumer_queue.put({
                "id": self.id,
                "original": msg,
                "translated": translatedMsg
            })