'''{"type":"adli_abstraction_id","value":"0-1"}'''
import sys

'''{"type":"adli_abstraction_id","value":"1"}'''
def place_books_on_shelf_from_basket(book_shelf, basket):

    '''{"type":"adli_abstraction_id","value":"1-1"}'''
    while len(basket) > 0:
        
        '''{"type":"adli_abstraction_id","value":"1-1-1"}'''
        book = basket.pop()

        '''{"type":"adli_abstraction_id","value":"1-1-2"}'''
        print(f"Accepted book: {book['name']} (Genre: {book['genre']})")
        
        '''{"type":"adli_abstraction_id","value":"1-1-3"}'''
        firstLetter = book['name'][0]

        '''{"type":"adli_abstraction_id","value":"1-1-4"}'''
        if (firstLetter not in book_shelf):
            '''{"type":"adli_abstraction_id","value":"1-1-4-1"}'''
            book_shelf[firstLetter] = []
        else:
            '''{"type":"adli_abstraction_id","value":"1-1-5"}'''
            print("Slot for book already exists.")

        '''{"type":"adli_abstraction_id","value":"1-1-6"}'''
        book_shelf[firstLetter].append(book['name'])

    '''{"type":"adli_abstraction_id","value":"1-2"}'''
    return book_shelf


'''{"type":"adli_abstraction_id","value":"2"}'''
def accept_book():

    '''{"type":"adli_abstraction_id","value":"2-1"}'''
    print("\nEnter book details:")
        
    '''{"type":"adli_abstraction_id","value":"2-2"}'''
    name = input("Book name: ")

    '''{"type":"adli_abstraction_id","value":"2-3"}'''
    genre = input("Genre: ")

    '''{"type":"adli_abstraction_id","value":"2-4"}'''
    return {"name":name, "genre":genre}


'''{"type":"adli_abstraction_id","value":"3"}'''
def library_manager():

    '''{"type":"adli_abstraction_id","value":"3-1"}'''
    book_shelf = {}

    '''{"type":"adli_abstraction_id","value":"3-2"}'''
    basket = []

    '''{"type":"adli_abstraction_id","value":"3-3"}'''
    while True:
        
        '''{"type":"adli_abstraction_id","value":"3-3-1"}'''
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

        '''{"type":"adli_abstraction_id","value":"3-3-2"}'''
        if response == "a":

            '''{"type":"adli_abstraction_id","value":"3-3-2-1"}'''
            book_details = accept_book()

            '''{"type":"adli_abstraction_id","value":"3-3-2-2"}'''
            basket.append(book_details)
      
            '''{"type":"adli_abstraction_id","value":"3-3-2-3"}'''
            continue

        '''{"type":"adli_abstraction_id","value":"3-3-3"}'''
        if response == "p":

            '''{"type":"adli_abstraction_id","value":"3-3-3-1"}'''
            book_shelf = place_books_on_shelf_from_basket(book_shelf, basket)

            '''{"type":"adli_abstraction_id","value":"3-3-3-2"}'''
            continue

        '''{"type":"adli_abstraction_id","value":"3-3-4"}'''
        if response == "d":

            '''{"type":"adli_abstraction_id","value":"3-3-4-1"}'''
            print("\nBook Shelf:", book_shelf)

            '''{"type":"adli_abstraction_id","value":"3-3-4-2"}'''
            print("Basket:", basket)

            '''{"type":"adli_abstraction_id","value":"3-3-4-3"}'''
            continue

        '''{"type":"adli_abstraction_id","value":"3-3-5"}'''
        if response != "c" or response != "d" or response != "p":
        
            '''{"type":"adli_abstraction_id","value":"3-3-5-1"}'''
            break

    '''{"type":"adli_abstraction_id","value":"3-4"}'''
    print("\nExiting library manager, goodbye.")


'''{"type":"adli_abstraction_id","value":"0-2"}'''
if __name__ == "__main__":

    '''{"type":"adli_abstraction_id","value":"0-2-1"}'''
    sys.exit(library_manager())
     