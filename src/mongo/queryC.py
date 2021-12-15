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
 

    c = db["citizen"].find({})
    citizen_df = pd.DataFrame(c)
    population = citizen_df.query("casref_do == '2020-12-31' & (vuzemi_cis == 101 | (vuzemi_cis ==  100 & vuzemi_txt == 'Hlavní město Praha')) & vek_kod.isnull() & pohlavi_kod.isnull()")
    o = population.drop(population.columns[[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]], axis=1)
    o = o.sort_values(by=["hodnota"], ascending=False)
    cities = list(o["vuzemi_txt"])[:50]
    population_to_15 = []
    population_15_to_60 = []
    population_over_60 = []
    first_quarter = []
    second_quarter = []
    third_quarter = []
    fourth_quarter = []
    
    print("Executing C request...")
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
        
        population_to_15.append(citizen_df.query("vuzemi_txt == '" + okres + "' & casref_do == '2020-12-31' & pohlavi_kod.isnull() & vek_kod <= 410010610015000")["hodnota"].sum())
        population_15_to_60.append(citizen_df.query("vuzemi_txt == '" + okres + "' & casref_do == '2020-12-31' & pohlavi_kod.isnull() & (vek_kod > 400000600005000 & vek_kod < 410060610065000)")["hodnota"].sum())
        population_over_60.append(citizen_df.query("vuzemi_txt == '" + okres + "' & casref_do == '2020-12-31' & pohlavi_kod.isnull() & vek_kod >= 410060610065000")["hodnota"].sum())
    
        #compute number of infections per quarter of year
        for i in range (1,5):

            df_quarter = df.loc[(df['datum'].dt.month == first) | 
                            (df['datum'].dt.month == second) |
                            (df['datum'].dt.month == third)]
            df_quarter = df_quarter.groupby(['okres_nazev']).sum()
            line_dt['okres'] = okres
            if(i == 1): first_quarter.append( int(df_quarter['nove_pripady']))
            if(i == 2): second_quarter.append( int(df_quarter['nove_pripady']))
            if(i == 3): third_quarter.append( int(df_quarter['nove_pripady']))
            if(i == 4): fourth_quarter.append( int(df_quarter['nove_pripady']))
            
            first += 3
            second += 3
            third += 3


    new = pd.DataFrame({
        "name": cities,
        "1. stvtrok nakazeny" : first_quarter,
        "2. stvtrok nakazeny" : second_quarter,
        "3. stvtrok nakazeny" : third_quarter,
        "4. stvtrok nakazeny" : fourth_quarter,
        "obyvatele_do_15": population_to_15,
        "obyvatele_15_do_60": population_15_to_60,
        "obyvatele_nad_60": population_over_60,
    })

    filePath = os.path.join('queries_csv', 'queryC.csv')
    new.to_csv(filePath)


