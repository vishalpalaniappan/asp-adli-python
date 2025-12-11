import queue
import time
import sys
import random
import threading
from BookShelfThread import BookShelfThread

def accept_book():

    print(f"\n{threading.get_ident()} Enter book details:")
        
    name = input(f"{threading.get_ident()} Book name: ")

    genre = input(f"{threading.get_ident()} Genre: ")

    book_details = {"name": name, "genre":genre}

    return book_details


def main(argv):
    message_queue = queue.Queue()
    BookShelfThread(1, message_queue)

    basket = []

    print(
        "\n==========================\n"\
        "         Main Thread Menu:\n" \
        "==========================\n"\
        "Enter a: Add book.\n" \
        "Enter p: Place books on shelf and continue.\n" \
        "Enter any other key: Exit\n" \
    )

    while True:
        response = input().lower()
        print(f"Option Selected: {response}")

        if response == "a":
            book_details = accept_book()
            basket.append(book_details)      
            continue

        elif response == "p":
            message_queue.put({
                "type": "add",
                "basket": basket
            })
            continue

        elif response == "d":
            message_queue.put({
                "type": "display",
                "basket": basket
            })
            continue

        else:
            break

        time.sleep(1)

if "__main__" == __name__:
    sys.exit(main(sys.argv))