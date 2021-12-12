
from download.constants import CITIZEN_URL, STATS, COVID_URL, CITIZEN_FILE_NAME,EPIDEMIC_STATS,TESTING,VACCINATION,OTHER
import requests
from bs4 import BeautifulSoup
import sys
import json
import os 


def covid_site(path_of_data):
    page = requests.get(COVID_URL,
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
        if key not in [COVID_URL+name for name in  os.listdir(path_of_data)]:
            to_be_downloaded.append(key)


    with open(os.path.join( path_of_data,'cache.json'), 'r', encoding='utf-8') as f:
        cache = dict(json.load(f))
    

    for x  in metadata_cache.keys():
        print(x)

        
    for key in cache.keys():
    
        if cache[key] != metadata_cache[key]:
            to_be_downloaded.append(key)
            cache[key] = metadata_cache[key]

    
    with open(os.path.join( path_of_data,'cache.json'), 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
    
    to_be_downloaded = list(set(to_be_downloaded))
    return to_be_downloaded







def citizen_site(path_to_data):
    page = requests.get(CITIZEN_URL,
                    headers={'Content-type': 'text/plain; charset=utf-8'})
    if page.status_code != 200:
        sys.exit("The page is not available")

    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find(id='main-content')
    soup = soup.find(id="column-1")
    soup = soup.find(id="layout-column_column-1")
    soup = soup.find(id="p_p_id_AttachmentsPortlet_WAR_rsprezentace_INSTANCE_tO9vjOXtGsJX_")
    soup = soup.find_all("li",class_="priloha")
    file_href = soup[-1].find("a")['href']
    date = soup[-1].find(class_="datum")
    date = date.text.split()[0]


    to_be_downloaded = []
    if CITIZEN_FILE_NAME not in os.listdir(path_to_data):
            to_be_downloaded.append(file_href)

    with open(os.path.join(path_to_data,'cache_citizen.json'), 'r', encoding='utf-8') as f:
        cache = dict(json.load(f))
        if cache[CITIZEN_FILE_NAME] != date:
            to_be_downloaded.append(file_href)

    to_be_downloaded = list(set(to_be_downloaded))
    return to_be_downloaded
