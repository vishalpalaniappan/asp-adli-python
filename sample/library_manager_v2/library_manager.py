'''{"type":"adli_abstraction_id","value":"1"}'''
import sys

'''{"type":"adli_abstraction_id","value":"2"}'''
def place_book_on_shelf(book_shelf, name, genre):

    '''{"type":"adli_abstraction_id","value":"3"}'''
    print(f"Accepted book: {name} (Genre: {genre})")
    
    '''{"type":"adli_abstraction_id","value":"4"}'''
    firstLetter = name[0].upper()

    '''{"type":"adli_abstraction_id","value":"5"}'''
    if (firstLetter not in book_shelf):
        '''{"type":"adli_abstraction_id","value":"6"}'''
        book_shelf[firstLetter] = []
    else:
        '''{"type":"adli_abstraction_id","value":"8"}'''
        print("Slot for book already exists.")

    '''{"type":"adli_abstraction_id","value":"9"}'''
    book_shelf[firstLetter].append(name)


'''{"type":"adli_abstraction_id","value":"10"}'''
def accept_book():

    '''{"type":"adli_abstraction_id","value":"11"}'''
    print("\nEnter book details:")
        
    '''{"type":"adli_abstraction_id","value":"12"}'''
    name = input("Book name: ")

    '''{"type":"adli_abstraction_id","value":"13"}'''
    genre = input("Genre: ")

    '''{"type":"adli_abstraction_id","value":"14"}'''
    return {"name":name, "genre":genre}


'''{"type":"adli_abstraction_id","value":"15"}'''
def library_manager():

    '''{"type":"adli_abstraction_id","value":"16"}'''
    book_shelf = {}

    '''{"type":"adli_abstraction_id","value":"17"}'''
    while True:

        '''{"type":"adli_abstraction_id","value":"18"}'''
        book_details = accept_book()

        '''{"type":"adli_abstraction_id","value":"19"}'''
        place_book_on_shelf(book_shelf, book_details["name"], book_details["genre"])
        
        '''{"type":"adli_abstraction_id","value":"20"}'''
        more = input("Add another book? (y): ").lower()
        
        '''{"type":"adli_abstraction_id","value":"21"}'''
        if more != "y":

            '''{"type":"adli_abstraction_id","value":"22"}'''
            break

    '''{"type":"adli_abstraction_id","value":"23"}'''
    print("Exiting library manager, goodbye.")


'''{"type":"adli_abstraction_id","value":"24"}'''
if __name__ == "__main__":

    '''{"type":"adli_abstraction_id","value":"25"}'''
    sys.exit(library_manager())
    