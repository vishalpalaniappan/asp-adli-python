import threading

class BookShelfThread(threading.Thread):
    def __init__(self, id, queue):
        super().__init__(daemon=True)
        self.book_shelf = {}
        self.queue = queue
        self.start()

    def __del__(self):
        print(f"{threading.get_ident()} Closed Thread", self.id)

    def place_books_on_shelf_from_basket(self, basket):

        while len(basket) > 0:
            book = basket.pop()

            print(f"{threading.get_ident()} Accepted book: {book['name']} (Genre: {book['genre']})")
            
            firstLetter = book['name'][0]

            if (firstLetter not in self.book_shelf):
                self.book_shelf[firstLetter] = []
            else:
                print(f"{threading.get_ident()} Slot for book already exists.")

            self.book_shelf[firstLetter].append(book['name'])


    def run(self):
        while True:
            if not self.queue.empty():
                msg = self.queue.get(timeout=0.5)

                if (msg["type"] == "add"):
                    self.place_books_on_shelf_from_basket(
                        msg["basket"]
                    )
                    continue
                elif (msg["type"] == "display"):
                    print(f"\n{threading.get_ident()} Book Shelf:", self.book_shelf)
                    print(f"{threading.get_ident()} Basket:", msg["basket"])
                    continue
