import threading
import queue

class BookShelfThread(threading.Thread):
    '''
    This class represents a bookshelf that exists on a separate thread.
    It listens for messages from the main thread via a message queue
    and performs operations such as adding books to the shelf and
    displaying the contents of the shelf.
    '''
    def __init__(self, queue):
        super().__init__(daemon=False)
        self.book_shelf = {}
        self.queue = queue
        self.start()

    def __del__(self):
        print(f"{threading.get_ident()} Terminating book shelf thread")

    def place_books_on_shelf_from_basket(self, basket):
        '''
        This function checks to see if there are books in the
        basket and places it on the shelf. It continues until
        there are no more books left.
        
        :param book_shelf: Object representing the bookshelf.
        :param basket: Array representing the basket.
        '''
        while len(basket) > 0:
            book = basket.pop()
            print(f"Processing Book: {book['name']} (Genre: {book['genre']})")
            
            firstLetter = book['name'][0]

            if (firstLetter not in self.book_shelf):
                self.book_shelf[firstLetter] = []

            self.book_shelf[firstLetter].append(book['name'])


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

            if (msg["type"] == "add"):
                print(f"\n")
                self.place_books_on_shelf_from_basket(
                    msg["basket"]
                )
            elif (msg["type"] == "display"):
                print(f"\n{threading.get_ident()} Book Shelf:", self.book_shelf)
                print(f"{threading.get_ident()} Basket:", msg["basket"])
            elif (msg["type"] == "quit"):
                break
