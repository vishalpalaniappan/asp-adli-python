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
            "intent":"Dictionary to group books by the first letter of their name."
        }
    }
'''
books_grouped_by_first_letter = {}


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
        },
        "dependencies":{
            "name":"string",
            "genre":"string"
        }
    }
}
'''
def sort_book(name, genre):
    '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Prints the accepted book details.",
                "dependencies":{
                    "name":"string",
                    "genre":"string"
                }
            }
        }
    '''
    print(f"Accepted book: {name} (Genre: {genre})")

    '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Get the first letter of the book name to group books.",
                "dependencies":{
                    "name":"string"
                },
                "constraints":{
                    "name":{
                        "type":"string",
                        "min_length":1,
                        "non_empty":true
                    }
                }
            }
        }
    '''
    firstLetter = name[0].upper()

    '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Get the dictionary to group books by first letter.",
            }
        }
    '''   
    global books_grouped_by_first_letter

    '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Check if the first letter key exists in the dictionary and initialize if not.",
                "dependencies":{
                    "firstLetter":"string",
                    "books_grouped_by_first_letter":"dictionary"
                },
                "constraints":{
                    "firstLetter":{
                        "type":"string",
                        "non_empty":true
                    },
                    "books_grouped_by_first_letter":{
                        "type":"dictionary" 
                    }
                }
            }
        }
    '''
    if (firstLetter not in books_grouped_by_first_letter):

        '''
            {
                "type":"adli_abstraction",
                "value":{
                    "intent":"Initialize the list for the first letter key in the dictionary."
                    "dependencies":{
                        "firstLetter":"string",
                        "books_grouped_by_first_letter":"dictionary"
                    }
                }
            }
        '''   
        books_grouped_by_first_letter[firstLetter] = []


    '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Append the book name to the corresponding first letter group in the dictionary."
                "dependencies":{
                    "firstLetter":"string",
                    "books_grouped_by_first_letter":"dictionary",
                    "name":"string"
                }
            }
        }
    '''   
    books_grouped_by_first_letter[firstLetter].append(name)




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
                    "min_length":1,
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
                    "min_length":1,
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
                },
                "dependencies":{
                    "sort_book":"function"
                    "name":"string",
                    "genre":"string"
                }
            }
        }
        '''
        sort_book(name, genre)

        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Ask user if they want to add another book by accepting 'y' or 'Y'. Any other input will stop the process."
                "constraint":{
                    "more": {
                        "type":"string",
                        "trueBranch":"y|Y",
                        "falseBranch":""
                    }
                }
            }
        }
        '''
        more = input("Add another book? (y): ").lower()
        
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
        "intent":"Entry point for the script.",
        "dependencies":{
            "__name__":"constant",
        }
    }
}
'''
if __name__ == "__main__":
    '''
    {
        "type":"adli_abstraction",
        "value":{
            "intent":"Call the function to accept books from user.",
            "dependencies":{
                "accept_books":"function"
                "sys":"module"
            }
        }
    }
    '''
    sys.exit(accept_books())
    