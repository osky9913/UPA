import os
import pandas as pd
from pymongo.database import Database

def convert_collection_to_csv(name, db : Database):
    print('Converting collection '+ name + ' to csv...')
    col = db[name]
    mongo_docs = col.find()
    # Convert the mongo docs to a DataFrame
    docs = pd.DataFrame(mongo_docs)
    # Discard the Mongo ID for the documents
    docs.pop("_id")

    output_dir = os.path.join('queries_csv')

    output_file = os.path.join(output_dir, name + '.csv')

    #with open(os.path.join(output_dir,output_file),'wb') as f: 
    docs.to_csv(output_file, ",", index=False) # CSV delimited by commas
    # export MongoDB documents to a CSV file, leaving out the row "labels" (row numbers)