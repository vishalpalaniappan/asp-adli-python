'''{"type":"adli_abstraction_id","value":"1"}'''
import sys

'''{"type":"adli_abstraction_id","value":"2"}'''
def place_books_on_shelf_from_basket(book_shelf, basket):

    '''{"type":"adli_abstraction_id","value":"3"}'''
    while len(basket) > 0:
        
        '''{"type":"adli_abstraction_id","value":"4"}'''
        book = basket.pop()

        '''{"type":"adli_abstraction_id","value":"5"}'''
        print(f"Accepted book: {book['name']} (Genre: {book['genre']})")
        
        '''{"type":"adli_abstraction_id","value":"6"}'''
        firstLetter = book['name'][0].upper()

        '''{"type":"adli_abstraction_id","value":"7"}'''
        if (firstLetter not in book_shelf):
            '''{"type":"adli_abstraction_id","value":"8"}'''
            book_shelf[firstLetter] = []
        else:
            '''{"type":"adli_abstraction_id","value":"9"}'''
            print("Slot for book already exists.")

        '''{"type":"adli_abstraction_id","value":"10"}'''
        book_shelf[firstLetter].append(book['name'])

    '''{"type":"adli_abstraction_id","value":"11"}'''
    return book_shelf


'''{"type":"adli_abstraction_id","value":"12"}'''
def accept_book():

    '''{"type":"adli_abstraction_id","value":"13"}'''
    print("\nEnter book details:")
        
    '''{"type":"adli_abstraction_id","value":"14"}'''
    name = input("Book name: ")

    '''{"type":"adli_abstraction_id","value":"15"}'''
    genre = input("Genre: ")

    '''{"type":"adli_abstraction_id","value":"16"}'''
    return {"name":name, "genre":genre}


'''{"type":"adli_abstraction_id","value":"17"}'''
def library_manager():

    '''{"type":"adli_abstraction_id","value":"18"}'''
    book_shelf = {}

    '''{"type":"adli_abstraction_id","value":"19"}'''
    basket = []

    '''{"type":"adli_abstraction_id","value":"20"}'''
    while True:
        
        '''{"type":"adli_abstraction_id","value":"21"}'''
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


        '''{"type":"adli_abstraction_id","value":"22"}'''
        if response == "a":

            '''{"type":"adli_abstraction_id","value":"23"}'''
            book_details = accept_book()

            '''{"type":"adli_abstraction_id","value":"24"}'''
            basket.append(book_details)
            
            '''{"type":"adli_abstraction_id","value":"25"}'''
            print("Book Shelf:", book_shelf)   
      
            '''{"type":"adli_abstraction_id","value":"26"}'''
            continue

        '''{"type":"adli_abstraction_id","value":"27"}'''
        if response == "p":

            '''{"type":"adli_abstraction_id","value":"28"}'''
            book_shelf = place_books_on_shelf_from_basket(book_shelf, basket)
            
            '''{"type":"adli_abstraction_id","value":"29"}'''
            print("Book Shelf:", book_shelf)

            '''{"type":"adli_abstraction_id","value":"30"}'''
            continue

        '''{"type":"adli_abstraction_id","value":"31"}'''
        if response == "d":

            '''{"type":"adli_abstraction_id","value":"32"}'''
            print("\nBook Shelf:", book_shelf)

            '''{"type":"adli_abstraction_id","value":"33"}'''
            print("Basket:", basket)

            '''{"type":"adli_abstraction_id","value":"34"}'''
            continue
    
        '''{"type":"adli_abstraction_id","value":"35"}'''
        break

    '''{"type":"adli_abstraction_id","value":"36"}'''
    print("\nExiting library manager, goodbye.")


'''{"type":"adli_abstraction_id","value":"37"}'''
if __name__ == "__main__":

    '''{"type":"adli_abstraction_id","value":"38"}'''
    sys.exit(library_manager())
    