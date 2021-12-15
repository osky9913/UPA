import os
from typing import ForwardRef
import pandas as pd
from pandas.core.frame import DataFrame
from mongo.mongo import import_collection
from pymongo.database import Database
from mongo.cities import OKRESY


def initialize_query_C(db: Database):
    osoby = pd.read_csv(os.path.join("data", "osoby.csv"))
    collection_dt = pd.DataFrame()
 
    for okres in OKRESY:
        line_dt = pd.DataFrame()
        #line_dt['okres'] = okres
        query = {'okres_nazev' : okres}
        #filter okresy from db
        col = db['obce'].find(query)

        #convert to dataframe
        df =  pd.DataFrame(list(col))
        #select only relevant columns
        df = df[['datum','okres_nazev','nove_pripady']]
        #select only year 2021
        df['datum'] = pd.to_datetime(df['datum'])
        df = df.loc[(df['datum'].dt.year == 2021)]

        first = 1
        second = 2
        third = 3
        df_quarter = pd.DataFrame()
        
        #compute number of infections per quarter of year
        for i in range (1,5):

            df_quarter = df.loc[(df['datum'].dt.month == first) | 
                            (df['datum'].dt.month == second) |
                            (df['datum'].dt.month == third)]
            df_quarter = df_quarter.groupby(['okres_nazev']).sum()
            line_dt['okres'] = okres
            line_dt["nakazeny za "+str(i)+".stvrtrok"]= df_quarter['nove_pripady']
            
            first += 3
            second += 3
            third += 3
        collection_dt = collection_dt.append(line_dt, ignore_index = True)
    
    print(collection_dt)
    filePath = os.path.join('queries_csv', 'queryC.csv')
    collection_dt.to_csv(filePath)