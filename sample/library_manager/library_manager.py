import sys
import uuid
import json

def place_books_on_shelf_from_basket(book_shelf, basket):
    '''
    This function checks to see if there are books in the
    basket and places it on the shelf. It continues until
    there are no more books left.
    
    :param book_shelf: Object representing the bookshelf.
    :param basket: Array representing the basket.
    '''
    while len(basket["value"]) > 0:
        book = basket["value"].pop()
        print(f"Accepted book: {book['value']['name']} (Genre: {book['value']['genre']})")
        
        firstLetter = book["value"]['name'][0]

        if (firstLetter not in book_shelf["value"]):
            book_shelf["value"][firstLetter] = []

        book_shelf["value"][firstLetter].append(book)

    return book_shelf

def accept_book():
    '''
    This function accepts the book from the user.
    '''
    print("\nEnter book details:")        
    name = input("Book name: ")
    genre = input("Genre: ")
    book_details = {"uid": str(uuid.uuid4()), "value": {"name": name, "genre":genre}}
    return book_details

def library_manager():
    '''
    This function serves the library manager. 

    It provides a menu that lets users add books to a basket and 
    place the books from the basket onto the shelf. It also allows
    the user to display the contents of the library and finally, it
    allows the user to exit the library.
    '''

    book_shelf = {"uid": str(uuid.uuid4()), "value":{}}

    basket = {"uid": str(uuid.uuid4()), "value":[]}

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
            basket["value"].append(book_details)

        elif response == "p":
            if (len(basket) > 5):
                raise Exception("Basket is too heavy, I can't bring it to the shelf.")
            book_shelf = place_books_on_shelf_from_basket(book_shelf, basket)

        elif response == "d":
            audit = {"uid": str(uuid.uuid4()), "value":{"Book Shelf": book_shelf, "Basket": basket}}
            print("\nLibrary Audit:", json.dumps(audit["value"], indent=2))

        else:        
            break

if __name__ == "__main__":
    sys.exit(library_manager())
     