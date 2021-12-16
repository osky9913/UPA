import os
import pandas as pd
from mongo.mongo import import_collection
from pymongo.database import Database
from mongo.mongo import import_collection
import matplotlib.pyplot as plt


CSV_FOLDER_NAME = "queries_csv"
DIAGRAMS_FOLDER_NAME = "img"
COLLECTION_NAME = "Vakciny"


def initialize_query_own(db: Database):
    osoby = pd.DataFrame(db["ockovani-zakladni-prehled"].find({}))
    osoby =  osoby.groupby(['vakcina']).size().to_frame('count').reset_index()
    osoby.to_csv(os.path.join(CSV_FOLDER_NAME, "vakciny.csv"), index=False)



def plot_vaccine_fig( ):
    df = pd.read_csv (os.path.join(CSV_FOLDER_NAME, "vakciny.csv"))
    labels = df['vakcina']
    sizes = df['count']
    explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
    shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig1.savefig(os.path.join(DIAGRAMS_FOLDER_NAME, "vaccine.png"))

