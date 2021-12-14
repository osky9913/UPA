# author:  Martin Osvald, Daniel Patek, David Spavor
from parser.parser import parse
from download.cache import covid_site, citizen_site
from download.constants import CITIZEN_FILE_NAME
from download.download import download
from mongo.mongo import initialize_mongo, import_csv_data
from mongo.queryA import initialize_query_A, export_A_csvs
from mongo.queryB import initialize_query_B
import os


def main():
    """
    The main function of the program
    """

    # path from makefile so if you want to run this src/main.py
    path_to_data = os.path.abspath(os.path.join(".", "data"))

    # download data
    list_of_files_to_be_download = covid_site(path_to_data)
    download(list_of_files_to_be_download, path_to_data)

    list_of_files_to_be_download = citizen_site(path_to_data)
    download(list_of_files_to_be_download, path_to_data, CITIZEN_FILE_NAME)

    # initialize mongo
    db = initialize_mongo()

    print('Importing raw csv files...')
    # import raw csv data
    import_csv_data(db)
    # initialize db for A query section
    initialize_query_A(db)
    # initialize db for B query section
    initialize_query_B(db)


if __name__ == "__main__":
    main()
