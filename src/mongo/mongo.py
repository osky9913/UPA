import collections
from pymongo import MongoClient
import pymongo, os, json, pandas
from pymongo.database import Database

#array of csv files, which will be imported to mongodb
csv_collection_names = ["nakazeni-vyleceni-umrti-testy",
                    "testy-pcr-antigenni",
                    "umrti",
                    "kraj-okres-nakazeni-vyleceni-umrti",
                    "kraj-okres-testy"]

def import_csv_data(db : Database):

    list_of_col = db.list_collection_names()
    #if db contains collections, drop them
    if(list_of_col != 0):
        for col in list_of_col:
            db.drop_collection(col)

    for col_name in csv_collection_names:
        #create collections 
        mycol = db[col_name]
        #insert data 
        data = pandas.read_csv(os.path.join("data", col_name + ".csv"))
        payload = json.loads(data.to_json(orient='records'))
        mycol.insert(payload)

    

def initialize_mongo():
    client = MongoClient()
    #create database
    db = client["upadb"]
    #load metada.json
    with open(os.path.join("data","metadata.json"),'rb') as f: 
        metadata = json.load(f)

    #iterate throug data and create collections specified by collection_names array and insert data
    #for url in metadata["Epidemiologické charakteristiky"]:
    #import data
    import_csv_data(db)
   

   