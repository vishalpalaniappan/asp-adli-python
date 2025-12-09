import sys

def place_book_on_shelf(book_shelf, name, genre):
    '''
    This function places the given book on the shelf 
    in a slot determined by the first letter of its name.
    
    :param book_shelf: Bookshelf to place the book on.
    :param name: Name of the book.
    :param genre: Genre of the book.
    '''
    print(f"Accepted book: {name} (Genre: {genre})")
    
    firstLetter = name[0].upper()

    if (firstLetter not in book_shelf):
        book_shelf[firstLetter] = []
    else:
        print("Slot for book already exists.")

    book_shelf[firstLetter].append(name)

    return book_shelf

def accept_book():
    '''
    Accepts a book and genre from the user and returns it.
    '''
    print("\nEnter book details:")
        
    name = input("Book name: ")

    genre = input("Genre: ")

    return {"name":name, "genre":genre}


def library_manager():
    '''
    Runs the library manager to accept books until the user decides to stop.
    '''
    book_shelf = {}

    while True:
        book_details = accept_book()
        book_shelf = place_book_on_shelf(
            book_shelf, 
            book_details["name"], 
            book_details["genre"]
        )

        more = input("Add another book? (y): ").lower()
        
        if more != "y":
            break

    print("Exiting library manager, goodbye.")

if __name__ == "__main__":
    sys.exit(library_manager())
    