# author:  Martin Osvald
from parser.parser import parse
from download.cache import cache
from download.download import download
from mongo.mongo import initialize_mongo
from mongo.queryA import initialize_query_A
import os

def main():
    """
    The main function of the program
    """

    #path from makefile so if you want to run this src/main.py
    path_to_data = os.path.abspath(os.path.join(".","data")) 

    #download data
    #list_of_files_to_be_download = cache(path_to_data) 
    #download(list_of_files_to_be_download,path_to_data)

    #initialize mongo
    #initialize_mongo()

    #initialize db for A query section
    initialize_query_A()
if __name__ == "__main__":
    main()
