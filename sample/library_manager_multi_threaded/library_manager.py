import queue
import sys
from book_shelf_thread import BookShelfThread

def accept_book():
    '''
    This function accepts the book from the user.
    '''
    print("\nEnter book details:")        
    name = input("Book name: ")
    genre = input("Genre: ")
    book_details = {"name": name, "genre":genre}
    return book_details

def library_manager():
    '''
    This function serves the library manager. 

    It provides a menu that lets users add books to a basket and 
    place the books from the basket onto the shelf. It also allows
    the user to display the contents of the library and finally, it
    allows the user to exit the library. The bookshelf exists on a 
    separate thread and the operations which concern it are
    communicated to it via a message queue.
    '''
    message_queue = queue.Queue()

    BookShelfThread(message_queue)

    basket = []

    while True:
        response = input(
            "\n==========================\n"\
            "      Main Thread Menu\n" \
            "==========================\n"\
            "Enter a: Add book.\n" \
            "Enter p: Place books on shelf and continue.\n" \
            "Enter d: Display contents of basket and book shelf.\n" \
            "Enter any other key: Exit\n"
        ).lower()

        if response == "a":
            book_details = accept_book()
            basket.append(book_details)   

        elif response == "p":
            message_queue.put({
                "type": "add",
                "basket": basket
            })
            basket = []      

        elif response == "d":
            message_queue.put({
                "type": "display",
                "basket": basket
            })   

        else:
            message_queue.put({
                "type": "quit"
            })
            break

if "__main__" == __name__:
    sys.exit(library_manager())