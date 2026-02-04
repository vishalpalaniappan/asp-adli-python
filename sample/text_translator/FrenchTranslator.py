import threading
import queue
from deep_translator import GoogleTranslator # type: ignore

class FrenchTranslator(threading.Thread):
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

            translatedMsg = GoogleTranslator(source="auto", target="french").translate(msg["data"])
            self.consumer_queue.put({
                "uid": msg["uid"],
                "language": "french",
                "original": msg["data"],
                "translated": translatedMsg
            })