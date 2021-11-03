import os, json
from typing import Collection
import pandas as pd
import pymongo
from mongo.mongo import import_collection
from pymongo.database import Database
from pymongo import MongoClient


COLLECTION_NAME = "kraje_rok_mesiac"
nuts_codes_citizen = {
    "CZ010": "3018",
    "CZ020": "3026",
    "CZ031": "3034",
    "CZ032": "3042",
    "CZ041": "3051",
    "CZ042": "3069",
    "CZ051": "3077",
    "CZ052": "3085",
    "CZ053": "3093",
    "CZ063": "3107",
    "CZ064": "3115",
    "CZ071": "3123",
    "CZ072": "3131",
    "CZ080": "3140"
}
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
    obyvatelstvo = pd.read_csv(os.path.join("data", "citizen.csv"))
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
                obj["kraj"] = nuts_codes[region]
                obj["kraj_nuts_code"] = region
                obj["kraj_populace"] = int(obyvatelstvo.query("vuzemi_kod==" + nuts_codes_citizen[region] + " & casref_do=='2020-12-31' & vek_kod.isnull() & pohlavi_kod.isnull()")["hodnota"].sum())
                obj["rok"] = int(year)
                obj["mesiac"] = int(month)
                #get number of infected people in specific region and in specific month
                obj["infekcie-za-mesiac"] = int(osoby.loc[(osoby['datum'].dt.year==year) & (osoby['datum'].dt.month==month) & (osoby['kraj_nuts_kod'] == region)].size)
                obj["ockovanie-za-mesiac"] = int(ockovani.loc[(ockovani['datum'].dt.year==year) & (ockovani['datum'].dt.month==month) & (ockovani['kraj_nuts_kod'] == region)].size)
                obj["smrti-za-mesiac"] = int(umrti.loc[(ockovani['datum'].dt.year==year) & (umrti['datum'].dt.month==month) & (umrti['kraj_nuts_kod'] == region)].size)
                collection.append(obj)
                
    import_collection(db, COLLECTION_NAME, collection)



    
    
    