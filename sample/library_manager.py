'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Import the operating system library.",
        "type":"leaf"
    }
}
'''
import sys

'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Function to sort a book based on its name and genre.",
        "type":"root",
        "node_type":"function_definition",
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
            "book_shelf":"dictionary",
            "name":"string",
            "genre":"string"
        }
    }
}
'''
def sort_book(book_shelf, name, genre):
    '''
    {
        "type":"adli_abstraction",
        "value":{
            "intent":"Prints the accepted book details.",
            "type":"leaf",
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
            "type":"leaf",
            "variables": {
                "firstLetter": "string"
            },
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
                "intent":"Check if the first letter key exists in the dictionary and initialize if not.",
                "type":"root",
                "node_type":"conditional",
                "dependencies":{
                    "firstLetter":"string",
                    "book_shelf":"dictionary"
                },
                "constraints":{
                    "firstLetter":{
                        "type":"string",
                        "non_empty":true
                    },
                    "book_shelf":{
                        "type":"dictionary" 
                    }
                }
            }
        }
    '''
    if (firstLetter not in book_shelf):

        '''
            {
                "type":"adli_abstraction",
                "value":{
                    "intent":"Initialize the list for the first letter key in the dictionary.",
                    "node_type":"conditional_branch",
                    "type":"leaf",
                    "dependencies":{
                        "firstLetter":"string",
                        "book_shelf":"dictionary"
                    }
                }
            }
        '''   
        book_shelf[firstLetter] = []


    '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Append the book name to the corresponding first letter group in the dictionary.",
                "type":"leaf",
                "dependencies":{
                    "firstLetter":"string",
                    "book_shelf":"dictionary",
                    "name":"string"
                }
            }
        }
    '''   
    book_shelf[firstLetter].append(name)




'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Accepts book details from user and sorts them.",
        "node_type":"function_definition",
        "type":"root"
    }
}
'''
def accept_books():

    '''
    {
        "type":"adli_abstraction",
        "value":{
            "intent":"Dictionary to group books by the first letter of their name.",
            "type":"leaf"
        }
    }
    '''
    book_shelf = {}


    '''
    {
        "type":"adli_abstraction",
        "value":{
            "intent":"Keep accepting books until the user decides to stop.",
            "type":"root",
            "node_type":"while_loop"
        }
    }
    '''
    while True:
        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Prompt user for book details.",
                "type":"leaf"
            }
        }
        '''
        print("\nEnter book details:")
        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Request book name from user.",
                "type":"leaf",
                "variables": {
                    "name": "string"
                },
                "constraint":{
                    "name": {
                        "type":"string",
                        "min_length":1,
                        "non_empty":true
                    }
                }                
            }
        }
        '''
        name = input("Book name: ")
        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Prompt genre of the book from user.",
                "type":"leaf",
                "variables": {
                    "genre": "string"
                },
                "constraint":{
                    "genre":{
                        "type":"string",
                        "min_length":1,
                        "non_empty":true
                    }
                }
            }
        }
        '''
        genre = input("Genre: ")

        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Call the sort function with the provided book details.",
                "type":"leaf",
                "function_calls": [
                    {
                        "function_name":"sort_book",
                        "arguments": {
                            "name":"name",
                            "genre":"genre"
                        }
                    }
                ],
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
                    "sort_book":"function",
                    "book_shelf":"dictionary",
                    "name":"string",
                    "genre":"string"
                }
            }
        }
        '''
        sort_book(book_shelf, name, genre)

        '''
        {
            "type":"adli_abstraction",
            "value":{
                "intent":"Ask user if they want to add another book by accepting 'y' or 'Y'. Any other input will stop the process.",
                "type":"leaf",
                "variables": {
                    "more": "string"
                },
                "constraint":{
                    "more": {
                        "type":"string"
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
                "intent":"Check if the user wants to stop adding books.",
                "type":"root",
                "node_type":"conditional",
                "dependencies":{
                    "more":"string"
                },
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
                    "intent":"Exit the book accepting loop.",
                    "type":"leaf"
                }
            }
            '''
            break


'''
{
    "type":"adli_abstraction",
    "value":{
        "intent":"Entry point for the script.",
        "type":"leaf",
        "node_type":"conditional_branch",
        "dependencies":{
            "__name__":"constant"
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
            "type":"leaf",
            "dependencies":{
                "accept_books":"function",
                "sys":"module"
            }
        }
    }
    '''
    sys.exit(accept_books())
    