import queue
import sys
import time
from Packer import PackerThread
from TamilTranslator import TamilTranslator
from FrenchTranslator import FrenchTranslator
from SpanishTranslator import SpanishTranslator

def TextTranslator():
    consumer_queue = queue.Queue()
    PackerThread(consumer_queue)

    message_queue_spanish = queue.Queue()
    message_queue_french = queue.Queue()
    message_queue_tamil = queue.Queue()

    SpanishTranslator(1, message_queue_spanish, consumer_queue)
    FrenchTranslator(2, message_queue_french, consumer_queue)
    TamilTranslator(3, message_queue_tamil, consumer_queue)

    while True:    
        data = input("\nEnter any string:")
        message_queue_spanish.put(data)
        message_queue_french.put(data)
        message_queue_tamil.put(data)
        time.sleep(1)

if "__main__" == __name__:
    sys.exit(TextTranslator())