from download.constants import STATS, URL, EPIDEMIC_STATS,TESTING,VACCINATION,OTHER
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import json
import os 




def cache(path_of_data) -> list : 
    """
    This function return a list of names of files which will be download
    """
    page = requests.get(URL,
                    headers={'Content-type': 'text/plain; charset=utf-8'})
    if page.status_code != 200:
        sys.exit("The page is not available")

    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find(id="react-app")
    metadata = json.loads(soup['data-datasets-metadata'])

    metadata_cache = {}
    for stat in STATS:
        for data in metadata[stat]:
            metadata_cache[data["url"]] = data["lastModification"]

    to_be_downloaded = []

    for key in metadata_cache.keys():
        if key not in os.listdir(path_of_data):
            to_be_downloaded.append(key)


    with open(os.path.join( path_of_data,'cache.json'), 'r', encoding='utf-8') as f:
        cache = dict(json.load(f))
    
    for key in cache.keys():
        if cache[key] != metadata_cache[key]:
            to_be_downloaded.append(key)
            cache[key] = metadata_cache[key]

    
    with open(os.path.join( path_of_data,'cache.json'), 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
    

    
    to_be_downloaded = list(set(to_be_downloaded))

    return to_be_downloaded


"""
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=4)
"""