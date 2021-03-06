import os
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core.indexes.range import RangeIndex
from mongo.mongo import import_collection
from pymongo.database import Database
from pandas.plotting import table
import numpy as np
from textwrap import wrap

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
    osoby = pd.DataFrame(db["osoby"].find({}))
    obyvatelstvo = pd.DataFrame(db["citizen"].find({}))
    regions = osoby["kraj_nuts_kod"].unique()
    regions = [k for k in regions if isinstance(k, str)]

    #obj = osoby.query('kraj_nuts_kod == "CZ010" & datum == "2021-03"')
    # convert dates to datetime for querying purposes
    osoby['datum'] = pd.to_datetime(osoby['datum'])

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
                obj["infekcie-za-mesiac"] = int(len(osoby.loc[(osoby['datum'].dt.year == year) & (
                    osoby['datum'].dt.month == month) & (osoby['kraj_nuts_kod'] == region)]))
                collection.append(obj)

    import_collection(db, COLLECTION_NAME, collection)


def plot_queries_B_ranking():
    filePath = os.path.join('queries_csv', "kraje_rok_mesiac.csv")
    df = pd.read_csv(filePath)
    osoby = pd.read_csv(os.path.join("data", "osoby.csv"))
    osoby['datum'] = pd.to_datetime(osoby['datum'])
    # filter 2021 year
    df = df.loc[(df['rok'] == 2021)]

    # aggregate months into 1/4 years
    new_df = pd.DataFrame()
    regions = df['kraj'].unique()
    for region in regions:
        region_df = df.loc[df['kraj'] == region]
        region_df = region_df.reset_index()
        d = {'kraj': 'last', 'mesiac': 'first', 'infekcie-za-mesiac': 'sum', 'kraj_populace': 'first'}
        region_df = region_df.groupby(region_df.index // 3).agg(d)
        new_df = new_df.append(region_df, ignore_index=True)

    # compute infection per one person
    new_df['pocet_nakazenych_na_obyvatela'] = round(new_df['infekcie-za-mesiac']/(new_df['kraj_populace']), 4)

    # filter each quarter year and sort values and plot rankinkgs for each quarter-year
    ranking4 = None
    quarter_year = 1
    for i in range(1, 5):
        ranking = new_df.loc[(new_df['mesiac'] == quarter_year)].sort_values(['pocet_nakazenych_na_obyvatela'])
        ranking = ranking[['kraj', 'infekcie-za-mesiac', 'kraj_populace', 'pocet_nakazenych_na_obyvatela']]
        ranking = ranking.reset_index()
        ranking = ranking.rename(columns={'infekcie-za-mesiac': 'infekcie-za-'+str(i)+'-stvrtrok'})
        del ranking['index']
        quarter_year += 3
        ranking4 = ranking
        plotRanking(ranking, i)

    # ranking 4 graph
    kraje = list(ranking4['kraj'].values)
    x_indexes = np.arange(len(kraje))
    infections = list(ranking4['infekcie-za-4-stvrtrok'].values)
    populace = list(ranking4['kraj_populace'].values)
    per_infections = list(ranking4['pocet_nakazenych_na_obyvatela'].values)
    barWidth = 0.3

    fig, ax = plt.subplots(figsize=(20, 8))
    plt.yscale('log')
    ax2 = ax.twinx()
    ax2.plot(x_indexes, per_infections, 'g-', label='infekcie na jedneho obyvatela kraja')
    ax.bar(x_indexes, populace, color="blue", width=barWidth, label="populace")
    ax.bar(x_indexes + barWidth, infections, color="red", width=barWidth, label="infekce za 4. stvrtrok")
    ax.set_ylabel('populace')
    ax2.set_ylabel('infekcie na jedneho obyvatela kraja')
    ax.set_xticks(x_indexes + barWidth / 2)
    kraje = ['\n'.join(wrap(l, 15)) for l in kraje]
    ax.set_xticklabels(kraje)

    ax.legend(loc='upper left')
    ax2.legend()
    plt.title("Pocet nakazenych za 4.stvrtrok 2021 v danom kraji v porovnani s poctom obyvatelov kraja.")
    plt.xlabel("Kraje")
    plt.tight_layout()
    filePath = os.path.join('img', 'graf-4-stvrtrok.png')
    plt.savefig(filePath, transparent=True, facecolor=fig.get_facecolor(), edgecolor='none')


def plotRanking(ranking, n):
    fig, ax = plt.subplots(figsize=(20, 5))
    fig.suptitle(str(n) + '. stvrtrok', fontsize=20)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)
    tabla = table(ax, ranking, loc='upper right', colWidths=[0.18]*len(ranking.columns))  # where df is your data frame
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(12)
    tabla.scale(1.5, 1.5)
    filePath = os.path.join('img', 'rebricek-' + str(n) + '-stvrtrok.png')
    plt.savefig(filePath, transparent=True, facecolor=fig.get_facecolor(), edgecolor='none')
