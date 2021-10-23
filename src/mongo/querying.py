from typing import Collection
from pymongo import MongoClient
def query_data(col:Collection):

    item_details = col.find({"datum" : "2021-02-10"})
    for item in item_details:
        # This does not give a very readable output
        print(item)
        

if __name__ == "__main__":
    client = MongoClient()
    #create database
    db = client["upadb"]
    col = db["testy-pcr-antigenni"]
    query_data(col)
