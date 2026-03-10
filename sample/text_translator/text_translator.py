import queue
import sys
import time
from Packer import PackerThread
from TamilTranslator import TamilTranslator
from FrenchTranslator import FrenchTranslator
from SpanishTranslator import SpanishTranslator
from TransactionDB import TransactionDB

def TextTranslator():
    packer_queue = queue.Queue()
    PackerThread(packer_queue)

    message_queue_spanish = queue.Queue()
    message_queue_french = queue.Queue()
    message_queue_tamil = queue.Queue()

    SpanishTranslator(1, message_queue_spanish, packer_queue)
    FrenchTranslator(2, message_queue_french, packer_queue)
    TamilTranslator(3, message_queue_tamil, packer_queue)

    db = TransactionDB()

    while True:    
        data = input("\nEnter any string:")
        job = db.addJob(data + "," + data)
        message_queue_spanish.put(job)
        message_queue_french.put(job)
        message_queue_tamil.put(job)
        time.sleep(1)

if "__main__" == __name__:
    sys.exit(TextTranslator())