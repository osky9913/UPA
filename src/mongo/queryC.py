import os
from typing import ForwardRef
import pandas as pd
from pandas.core.frame import DataFrame
from mongo.mongo import import_collection
from pymongo.database import Database
from mongo.cities import OKRESY
import matplotlib.pyplot as plt
import numpy as np

def initialize_query_C(db: Database):

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
    v_first_quarter = []
    v_second_quarter = []
    v_third_quarter = []
    v_fourth_quarter = []

    print("Executing C request...")
    for okres in OKRESY:
        okres2 = okres
        print("Okres: " + okres)

        subs_list = ["Hlavní město Praha", "Brno-město", "Ostrava-město", "Brno-venkov", "Praha-východ", "Praha-západ", "Plzeň-město"]
        if okres in subs_list:
            for s in ["Hlavní město ", "-město", "-venkov", "-východ", "-západ"]:
                okres2 = okres2.replace(s, "")

        ockovani = pd.DataFrame(db['ockovani-geografie'].find({'orp_bydliste': okres2}))
        if(len(list(ockovani)) == 0):
            print(okres2)
        ockovani['datum'] = pd.to_datetime(ockovani['datum'])

        ockovani = ockovani.loc[(ockovani['datum'].dt.year == 2021)]

        #line_dt['okres'] = okres
        query = {'okres_nazev': okres}
        # filter okresy from db
        col = db['obce'].find(query)

        # convert to dataframe
        df = pd.DataFrame(list(col))
        # select only relevant columns
        df = df[['datum', 'okres_nazev', 'nove_pripady']]
        ockovani = ockovani[['datum', 'orp_bydliste', 'pocet_davek']]
        # select only year 2021
        df['datum'] = pd.to_datetime(df['datum'])
        df = df.loc[(df['datum'].dt.year == 2021)]

        first = 1
        second = 2
        third = 3
        df_quarter = pd.DataFrame()
        dv_quarter = pd.DataFrame()

        population_to_15.append(citizen_df.query("vuzemi_txt == '" + okres + "' & casref_do == '2020-12-31' & pohlavi_kod.isnull() & vek_kod <= 410010610015000")["hodnota"].sum())
        population_15_to_60.append(citizen_df.query("vuzemi_txt == '" + okres + "' & casref_do == '2020-12-31' & pohlavi_kod.isnull() & (vek_kod > 400000600005000 & vek_kod < 410060610065000)")["hodnota"].sum())
        population_over_60.append(citizen_df.query("vuzemi_txt == '" + okres + "' & casref_do == '2020-12-31' & pohlavi_kod.isnull() & vek_kod >= 410060610065000")["hodnota"].sum())

        # compute number of infections per quarter of year
        for i in range(1, 5):

            df_quarter = df.loc[(df['datum'].dt.month == first) |
                                (df['datum'].dt.month == second) |
                                (df['datum'].dt.month == third)]
            dv_quarter = ockovani.loc[(ockovani['datum'].dt.month == first) | (ockovani['datum'].dt.month == second) | (ockovani['datum'].dt.month == third)]
            df_quarter = df_quarter.groupby(['okres_nazev']).sum()
            dv_quarter = dv_quarter.groupby(['orp_bydliste']).sum()
            if(i == 1):
                first_quarter.append(int(df_quarter['nove_pripady']))
                v_first_quarter.append(int(dv_quarter['pocet_davek']))

            if(i == 2):
                second_quarter.append(int(df_quarter['nove_pripady']))
                v_second_quarter.append(int(dv_quarter['pocet_davek']))
            if(i == 3):
                third_quarter.append(int(df_quarter['nove_pripady']))
                v_third_quarter.append(int(dv_quarter['pocet_davek']))
            if(i == 4):
                fourth_quarter.append(int(df_quarter['nove_pripady']))
                v_fourth_quarter.append(int(dv_quarter['pocet_davek']))

            first += 3
            second += 3
            third += 3

    # normalization
    print("Data normalization...")
    first_quarter = normalize(first_quarter)
    second_quarter = normalize(second_quarter)
    third_quarter = normalize(third_quarter)
    fourth_quarter = normalize(fourth_quarter)

    # discretization
    print("Data discretization...")
    population_over_60 = discretize(population_over_60)

    # detection of outliers
    print("Detection of outliers...")
    interquartile_detection(population_to_15)
    
    new = pd.DataFrame({
        "name": cities,
        "1. stvtrok nakazeny": first_quarter,
        "2. stvtrok nakazeny": second_quarter,
        "3. stvtrok nakazeny": third_quarter,
        "4. stvtrok nakazeny": fourth_quarter,
        "1. stvtrok ockovany": v_first_quarter,
        "2. stvtrok ockovany": v_second_quarter,
        "3. stvtrok ockovany": v_third_quarter,
        "4. stvtrok ockovany": v_fourth_quarter,
        "obyvatele_do_15": population_to_15,
        "obyvatele_15_do_60": population_15_to_60,
        "obyvatele_nad_60": population_over_60,
    })

    filePath = os.path.join('queries_csv', 'queryC.csv')
    new.to_csv(filePath)


def normalize(data):
    min_h = min(data)
    max_h = max(data)
    new = []
    for i in data:
        new.append(((i - min_h)/(max_h - min_h)) * (1 - 0) + 0)
    return new

def get_category(value):

    if 0 <= value <= 9999:
        return 'A'
    elif 10000 <= value <= 19999:
        return 'B'
    elif 20000 <= value <= 29999:
        return 'C'
    elif 30000 <= value <= 39999:
        return 'D'
    elif 40000 <= value <= 49999:
        return 'E'
    else:
        return 'F'


def discretize(data):
    new = []
    for i in data:
        new.append(get_category(i))
    return new

def interquartile_detection(data):

    name = 'obyvatele_do_15'
    dt = pd.DataFrame({name:data})
   
    #compute quantiles
    q1 = dt[name].quantile(0.25)
    q3 = dt[name].quantile(0.75)
    #compute iqr
    iqr = q3 - q1
    new = dt[np.logical_or(dt[name] < (q1 - 1.5*iqr),dt[name] > (q3 + 1.5*iqr))]
    filePath = os.path.join('queries_csv', 'outliers.csv')
    new.to_csv(filePath)
   
    # new = []
    # for i in data:
    #     new.append(get_category(i))
    # return new
