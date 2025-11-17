'''{"type":"adli_abstraction","value":{"intent":"import the operating system library"}}'''
import os

'''{"type":"adli_abstraction","value":{"intent":"function to create a directory if it does not exist"}}'''
def create_output_directory(path):
    '''{"type":"adli_abstraction","value":{"intent":"check if the path exists and create it if not"}}'''
    if not os.path.exists(path):
        '''{"type":"adli_abstraction","value":{"intent":"create the directory at the specified path"}}'''
        os.makedirs(path)


'''{"type":"adli_abstraction","value":{"intent":"entry point for the script"}}'''
if __name__ == "__main__":
    '''{"type":"adli_abstraction","value":{"intent":"define the output directory"}}'''
    output_dir = "output_logs"
    '''{"type":"adli_abstraction","value":{"intent":"create the output directory"}}'''
    create_output_directory(output_dir)