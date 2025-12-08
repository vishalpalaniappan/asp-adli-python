'''{"type":"adli_abstraction_id","value":"0-1"}'''
import sys

'''{"type":"adli_abstraction_id","value":"1"}'''
def place_book_on_shelf(book_shelf, name, genre):

    '''{"type":"adli_abstraction_id","value":"1-1"}'''
    print(f"Accepted book: {name} (Genre: {genre})")
    
    '''{"type":"adli_abstraction_id","value":"1-2"}'''
    firstLetter = name[0].upper()

    '''{"type":"adli_abstraction_id","value":"1-3"}'''
    if (firstLetter not in book_shelf):

        '''{"type":"adli_abstraction_id","value":"1-3-1"}'''
        book_shelf[firstLetter] = []
    else:

        '''{"type":"adli_abstraction_id","value":"1-4"}'''
        print("Slot for book already exists.")

    '''{"type":"adli_abstraction_id","value":"1-5"}'''
    book_shelf[firstLetter].append(name)

    '''{"type":"adli_abstraction_id","value":"1-6"}'''
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
    while True:

        '''{"type":"adli_abstraction_id","value":"3-2-1"}'''
        book_details = accept_book()

        '''{"type":"adli_abstraction_id","value":"3-2-2"}'''
        book_shelf = place_book_on_shelf(book_shelf, book_details["name"], book_details["genre"])
        
        '''{"type":"adli_abstraction_id","value":"3-2-3"}'''
        more = input("Add another book? (y): ").lower()
        
        '''{"type":"adli_abstraction_id","value":"3-2-4"}'''
        if more != "y":

            '''{"type":"adli_abstraction_id","value":"3-2-4-1"}'''
            break

    '''{"type":"adli_abstraction_id","value":"3-3"}'''
    print("Exiting library manager, goodbye.")


'''{"type":"adli_abstraction_id","value":"0-2"}'''
if __name__ == "__main__":

    '''{"type":"adli_abstraction_id","value":"0-2-1"}'''
    sys.exit(library_manager())
    