# author: Martin Osvald
import requests
import os

def download(to_be_downloaded: list, where: str , name=None):
    """
    Function for downloading datasets from URL constans
    """

    for csv_url in to_be_downloaded:
        
        # csv_url = URL + file

        if name == None:
            file = csv_url.split('/')[-1]
        else: 
            file = name


        print("Downloading ", csv_url)
        req = requests. get(csv_url)
        url_content = req.content


        csv_file = open( os.path.join(where,file), 'wb')
        csv_file.write(url_content)
        csv_file.close()
