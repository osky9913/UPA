import os, json
from typing import Collection
import pandas as pd
import pymongo
from mongo.mongo import import_collection
from pymongo.database import Database
from pymongo import MongoClient


COLLECTION_NAME = "kraje_rok_mesiac"

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
    ockovani = pd.read_csv(os.path.join("data", "ockovani.csv"))
    umrti = pd.read_csv(os.path.join("data", "umrti.csv"))
    regions = osoby["kraj_nuts_kod"].unique()

    obj = osoby.query('kraj_nuts_kod == "CZ010" & datum == "2021-03"')
    #convert dates to datetime for querying purposes
    osoby['datum'] = pd.to_datetime(osoby['datum'])
    ockovani['datum'] = pd.to_datetime(ockovani['datum'])
    umrti['datum'] = pd.to_datetime(umrti['datum'])

    #get years of pandemic from data
    years_of_pandemic = osoby['datum'].dt.year.unique()

    
    collection = []

    for region in regions:
        for year in years_of_pandemic:
            for month in range(1,13):  
                print("Dotazy_B: Processing data for:" ,year, "-", month , " ", nuts_codes[region])      
                obj = {}
                obj["region"] = nuts_codes[region]
                obj["region_nuts_code"] = region
                obj["year"] = int(year)
                obj["month"] = int(month)
                #get number of infected people in specific region and in specific month
                obj["per-month-infections"] = int(osoby.loc[(osoby['datum'].dt.year==year) & (osoby['datum'].dt.month==month) & (osoby['kraj_nuts_kod'] == region)].size)
                obj["per-month-vaccinated"] = int(ockovani.loc[(ockovani['datum'].dt.year==year) & (ockovani['datum'].dt.month==month) & (ockovani['kraj_nuts_kod'] == region)].size)
                obj["per-month-deaths"] = int(umrti.loc[(ockovani['datum'].dt.year==year) & (umrti['datum'].dt.month==month) & (umrti['kraj_nuts_kod'] == region)].size)
                collection.append(obj)
                
    import_collection(db, COLLECTION_NAME, collection)



    
    
    