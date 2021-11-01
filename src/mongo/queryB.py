import os, json
import pandas as pd
import pymongo
from mongo import import_collection
from pymongo.database import Database
from pymongo import MongoClient


COLLECTION_NAME = "kraje_mesiac"

nuts_codes = {
    "CZ010": "Hlavní město Praha",
    "CZ020": "Středočeský kraj",
    "CZ031": "Jihočeský kraj",
    "CZ032": "Plzeňský kraj",
    "CZ041": "Karlovarský kraj",
    "CZ042": "Ústecký kraj",
    "CZ051": "Liberecký kraj",
    "CZ052": "Královéhradecký kraj",
    "CZ053": "Pardubický kraj",
    "CZ063": "Kraj Vysočina",
    "CZ064": "Jihomoravský kraj",
    "CZ071": "Olomoucký kraj",
    "CZ072": "Zlínský kraj",
    "CZ080": "Moravskoslezský kraj"
}


def initialize_query_B(db: Database):
    osoby = pd.read_csv(os.path.join("data", "osoby.csv"))
    regions = osoby["kraj_nuts_kod"].unique()

    obj = osoby.query('kraj_nuts_kod == "CZ010" & datum == "2021-03"')
    #convert dates to datetime for querying purposes
    osoby['datum'] = pd.to_datetime(osoby['datum'])

    #get years of pandemic from data
    years_of_pandemic = osoby['datum'].dt.year.unique()

    
    final_array = []

    for region in regions:
        for year in years_of_pandemic:
            for month in range(1,13):  
                print("Dotazy_B: Processing data for:" ,year, "-", month , " ", nuts_codes[region])      
                obj = {}
                obj["year"] = int(year)
                obj["month"] = int(month)
                obj["region"] = nuts_codes[region]
                obj["region_nuts_code"] = region
                #get number of infected people in specific region and in specific month
                obj["per-month-infections"] = int(osoby.loc[(osoby['datum'].dt.year==year) & (osoby['datum'].dt.month==month) & (osoby['kraj_nuts_kod'] == region)].size)
                final_array.append(obj)
                
        

        
        

    import_collection(db, COLLECTION_NAME, final_array)


if __name__ == "__main__":
    client = MongoClient()
    db = client["upadb"]
    
    initialize_query_B(db)
    