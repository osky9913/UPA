# author: Martin Osvald
from download.constants import  URL
import requests
import os

def download(to_be_downloaded: list, where: str):
    """
    Function for downloading datasets from URL constans
    """

    for file in to_be_downloaded:
        csv_url = URL + file
        print("Downloading ", csv_url)
        req = requests. get(csv_url)
        url_content = req.content
        csv_file = open( os.path.join(where,file), 'wb')
        csv_file.write(url_content)
        csv_file.close()
