import sys

def place_books_on_shelf_from_basket(book_shelf, basket):

    while len(basket) > 0:
        book = basket.pop()

        print(f"Accepted book: {book['name']} (Genre: {book['genre']})")
        
        firstLetter = book['name'][0]

        if (firstLetter not in book_shelf):
            book_shelf[firstLetter] = []
        else:
            print("Slot for book already exists.")

        book_shelf[firstLetter].append(book['name'])

    return book_shelf

def accept_book():

    print("\nEnter book details:")
        
    name = input("Book name: ")

    genre = input("Genre: ")

    book_details = {"genre":genre}

    return book_details

def library_manager():

    book_shelf = {}

    basket = []

    while True:
        
        response = input(
            "\n==========================\n"\
            "         Menu:\n" \
            "==========================\n"\
            "Enter a: Add book.\n" \
            "Enter p: Place books on shelf and continue.\n" \
            "Enter d: Display contents of basket and book shelf.\n" \
            "Enter any other key: Exit\n" \
            "\nResponse:"
        ).lower()

        if response == "a":

            book_details = accept_book()

            basket.append(book_details)
      
            continue

        elif response == "p":

            book_shelf = place_books_on_shelf_from_basket(book_shelf, basket)

            continue

        elif response == "d":

            print("\nBook Shelf:", book_shelf)

            print("Basket:", basket)

            continue

        else:
        
            break

    print("\nExiting library manager, goodbye.")

if __name__ == "__main__":
    sys.exit(library_manager())
     