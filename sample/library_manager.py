'''{"type":"adli_abstraction_id","value":"1"}'''
import sys

'''{"type":"adli_abstraction_id","value":"2"}'''
def sort_book(book_shelf, name, genre):

    '''{"type":"adli_abstraction_id","value":"3"}'''
    print(f"Accepted book: {name} (Genre: {genre})")
    
    '''{"type":"adli_abstraction_id","value":"4"}'''
    firstLetter = name[0].upper()

    '''{"type":"adli_abstraction_id","value":"5"}'''
    if (firstLetter not in book_shelf):
        
        '''{"type":"adli_abstraction_id","value":"6"}'''
        book_shelf[firstLetter] = []

    '''{"type":"adli_abstraction_id","value":"7"}'''
    book_shelf[firstLetter].append(name)


'''{"type":"adli_abstraction_id","value":"8"}'''
def accept_books():

    '''{"type":"adli_abstraction_id","value":"9"}'''
    book_shelf = {}

    '''{"type":"adli_abstraction_id","value":"10"}'''
    while True:

        '''{"type":"adli_abstraction_id","value":"11"}'''
        print("\nEnter book details:")
        
        '''{"type":"adli_abstraction_id","value":"12"}'''
        name = input("Book name: ")

        '''{"type":"adli_abstraction_id","value":"13"}'''
        genre = input("Genre: ")

        '''{"type":"adli_abstraction_id","value":"14"}'''
        sort_book(book_shelf, name, genre)
        
        '''{"type":"adli_abstraction_id","value":"15"}'''
        more = input("Add another book? (y): ").lower()
        
        '''{"type":"adli_abstraction_id","value":"16"}'''
        if more != "y":

            '''{"type":"adli_abstraction_id","value":"17"}'''
            break

'''{"type":"adli_abstraction_id","value":"18"}'''
if __name__ == "__main__":

    '''{"type":"adli_abstraction_id","value":"19"}'''
    sys.exit(accept_books())
    