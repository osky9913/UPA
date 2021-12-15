from pymongo import MongoClient
import os
import json
import pandas
from pymongo.database import Database


# array of csv files, which will be imported to mongodb
csv_collection_names = ["osoby", "ockovani-zakladni-prehled", "obce","citizen"]


def import_csv_data(db: Database):

    list_of_col = db.list_collection_names()
    # if db contains collections, drop them
    if(list_of_col != 0):
        for col in list_of_col:
            db.drop_collection(col)

    for col_name in csv_collection_names:
        print("Importing " +col_name+".csv")
        # create collections
        mycol = db[col_name]
        # insert data
        data = pandas.read_csv(os.path.join("data", col_name + ".csv"))
        payload = json.loads(data.to_json(orient='records'))
        mycol.insert(payload)


def initialize_mongo():
    """Creates new instance of Mongo database and returns it.
    """

    client = MongoClient()
    db = client["upadb"]
    return db


def import_collection(db: Database, collection_name, data):
    """Creates new collection or updates existing collection in db.
    Does nothing when db is null or name is empty.
    """

    if db is None or collection_name == "":
        return

    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

    collection = db[collection_name]
    collection.insert(data)
