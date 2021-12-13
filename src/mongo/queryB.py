import os
import pandas as pd
import matplotlib.pyplot as plt 
from mongo.mongo import import_collection
from pymongo.database import Database
from pandas.plotting import table


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
    regions = [k for k in regions if isinstance(k, str)]

    obj = osoby.query('kraj_nuts_kod == "CZ010" & datum == "2021-03"')
    # convert dates to datetime for querying purposes
    osoby['datum'] = pd.to_datetime(osoby['datum'])
    ockovani['datum'] = pd.to_datetime(ockovani['datum'])
    umrti['datum'] = pd.to_datetime(umrti['datum'])

    # get years of pandemic from data
    years_of_pandemic = osoby['datum'].dt.year.unique()

    collection = []

    for region in regions:
        for year in years_of_pandemic:
            for month in range(1, 13):
                print("Requests_B: Processing data for:", year,
                      "-", month, " ", nuts_codes[region])
                obj = {}
                obj["kraj"] = nuts_codes[region]
                obj["kraj_nuts_code"] = region
                obj["kraj_populace"] = int(obyvatelstvo.query("vuzemi_kod==" + nuts_codes_citizen[region] +
                                           " & casref_do=='2020-12-31' & vek_kod.isnull() & pohlavi_kod.isnull()")["hodnota"].sum())
                obj["rok"] = int(year)
                obj["mesiac"] = int(month)
                # get number of infected people in specific region and in specific month
                obj["infekcie-za-mesiac"] = int(osoby.loc[(osoby['datum'].dt.year == year) & (
                    osoby['datum'].dt.month == month) & (osoby['kraj_nuts_kod'] == region)].size)
                obj["ockovanie-za-mesiac"] = int(ockovani.loc[(ockovani['datum'].dt.year == year) & (
                    ockovani['datum'].dt.month == month) & (ockovani['kraj_nuts_kod'] == region)].size)
                obj["smrti-za-mesiac"] = int(umrti.loc[(ockovani['datum'].dt.year == year) & (
                    umrti['datum'].dt.month == month) & (umrti['kraj_nuts_kod'] == region)].size)
                collection.append(obj)

    import_collection(db, COLLECTION_NAME, collection)


def queryB(csvFileName):
    filePath = os.path.join('queries_csv',csvFileName)
    df = pd.read_csv(filePath)
    #print(df.head(5))

    #filter 2021 year
    df = df.loc[(df['rok'] == 2021)]
    #print(df[['kraj_populace', 'infekcie-za-mesiac',]])

    #compute infections per one inhabitant in region
    df['pocet_nakazenych_na_obyvatela'] = df['infekcie-za-mesiac'] / df['kraj_populace'] 
    #print(df.head(13))


    #aggregate months into 1/4 years
    df = df.reset_index()
    d = {'kraj': 'last', 'mesiac': 'first', 'infekcie-za-mesiac':'sum' ,'kraj_populace':'first','pocet_nakazenych_na_obyvatela': 'sum'}
    df = df.groupby(df.index // 3).agg(d) 
    #print(df)


    #filter each quarter year and sort values
    ranking1 = df.loc[(df['mesiac'] == 1)].sort_values(['pocet_nakazenych_na_obyvatela'])
    ranking1 = ranking1[['kraj', 'infekcie-za-mesiac','kraj_populace','pocet_nakazenych_na_obyvatela']]
    ranking1 = ranking1.reset_index()
    del ranking1['index']

    print(ranking1)


    fig, ax = plt.subplots(figsize=(20, 5)) # set size frame
    fig.suptitle('1. stvrtrok', fontsize=20)
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
    tabla = table(ax, ranking1, loc='upper right', colWidths=[0.18]*len(ranking1.columns))  # where df is your data frame
    tabla.auto_set_font_size(False) # Activate set fontsize manually
    tabla.set_fontsize(12) # if ++fontsize is necessary ++colWidths
    tabla.scale(1.5, 1.5) # change size table
    plt.savefig('ranking1.png', transparent=True)

    