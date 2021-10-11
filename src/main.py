# author:  Martin Osvald
from parser.parser import parse
from download.cache import cache
from download.download import download
import os

def main():
    """
    The main function of the program
    """

    #path from makefile so if you want to run this src/main.py
    path_to_data = os.path.abspath(os.path.join(".","data")) 

    list_of_files_to_be_download = cache(path_to_data) 
    download(list_of_files_to_be_download,path_to_data)

if __name__ == "__main__":
    main()
