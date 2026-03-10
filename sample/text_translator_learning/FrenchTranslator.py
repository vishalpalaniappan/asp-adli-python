import threading
import queue
from deep_translator import GoogleTranslator # type: ignore

class FrenchTranslator(threading.Thread):
    def __init__(self, id, queue, packerQueue):
        super().__init__(daemon=True)
        self.queue = queue
        self.id = id
        self.packerQueue = packerQueue
        self.start()

    def run(self):
        while True:
            try:
                job = self.queue.get(timeout=10)
            except queue.Empty:
                continue

            translatedMsg = GoogleTranslator(source="auto", target="french").translate(job["value"]["data"])
            self.packerQueue.put({
                "uid": job["uid"],
                "value": {
                    "language": "french",
                    "original": job["value"]["data"],
                    "translated": translatedMsg
                }
            })