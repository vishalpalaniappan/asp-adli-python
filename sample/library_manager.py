'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Import the operating system library."
    }
}
'''
import sys


'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Function to sort a book based on its name and genre."
        "constraint":{
            "name":{
                "type":"string",
                "non_empty":true
            },
            "genre":{
                "type":"string",
                "non_empty":true
            }
        }
    }
}
'''
def sort_book(name, genre):
    '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Prints the accepted book details."
            }
        }
        '''
    print(f"Accepted book: {name} (Genre: {genre})")


'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Accepts book details from user and sorts them."
    }
}
'''
def accept_books():
    '''
    {
        "type":"adli_abstraction",
        "value":{
            "intent":"Keep accepting books until the user decides to stop."
        }
    }
    '''
    while True:
        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Prompt user for book details."
            }
        }
        '''
        print("\nEnter book details:")
        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Request book name from user."
                "constraint":{
                    "type":"string",
                    "non_empty":true
                }                
            }
        }
        '''
        name = input("Book name: ")
        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Prompt genre of the book from user."
                "constraint":{
                    "type":"string",
                    "non_empty":true
                }
            }
        }
        '''
        genre = input("Genre: ")

        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Call the sort function with the provided book details."
                "constraint":{
                    "name":{
                        "type":"string",
                        "non_empty":true
                    },
                    "genre":{
                        "type":"string",
                        "non_empty":true
                    }
                }
            }
        }
        '''
        sort_book(name, genre)

        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Ask user if they want to add another book."
                "constraint":{
                    "more": {
                        "type":"string"
                    }
                }
            }
        }
        '''
        more = input("Add another book? (y/n): ").lower()
        
        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Check if the user wants to stop adding books."
                "constraint":{
                    "more": {
                        "type":"string"
                    }
                }
            }
        }
        '''
        if more != "y":

            '''
            {
                "type":"adli_abstraction",
                "value":{
                    "intent":"Exit the book accepting loop."
                }
            }
            '''
            break


'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Entry point for the script."
    }
}
'''
if __name__ == "__main__":
    '''
    {
        "type":"adli_abstraction",
        "value":{
            "intent":"Call the function to accept books from user."
        }
    }
    '''
    sys.exit(accept_books())
    