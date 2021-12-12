import os
import pandas
from mongo.mongo import import_collection
from pymongo.database import Database

COLLECTION_NAME = "kraje_celkove"

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

vekove_skupiny = [
    {
        "query": "vek < 25",
        "query_ockovani": "& (vekova_skupina == '12-15' | vekova_skupina == '16-17' | vekova_skupina == '18-24')",
        "nazev": "0-24"
    },
    {
        "query": "vek > 24 & vek < 60",
        "query_ockovani": "& (vekova_skupina != '60-64' & vekova_skupina != '65-69' & vekova_skupina != '70-74' & vekova_skupina != '75-79' & vekova_skupina != '80+' & vekova_skupina != '12-15' & vekova_skupina != '16-17' & vekova_skupina != '18-24')",
        "nazev": "25-59"
    },
    {
        "query": "vek > 59",
        "query_ockovani": "& (vekova_skupina == '60-64' | vekova_skupina == '65-69' | vekova_skupina == '70-74' | vekova_skupina == '75-79'| vekova_skupina == '80+')",
        "nazev": "60-150"
    }
]


def initialize_query_A(db: Database):
    """Initialize data for section A in project assigment.
    For each province in Czechia process numbers needed for further querying.
    Then upload documents to db.
    """

    # read the CSV files
    osoby_nakazeni = pandas.read_csv(os.path.join("data", "osoby.csv"))
    osoby_ockovani = pandas.read_csv(os.path.join(
        "data", "ockovani-zakladni-prehled.csv"))
    obyvatelstvo = pandas.read_csv(os.path.join("data", "citizen.csv"))

    # get numbers of provinces
    kraje = osoby_nakazeni["kraj_nuts_kod"].unique()
    kraje = [k for k in kraje if isinstance(k, str)]
    final_array = []

    for kraj in kraje:
        print("Requests_A: Processing data for: " + nuts_codes[kraj])
        obj = {}
        obj["id"] = kraj
        obj["nazev_kraje"] = nuts_codes[kraj]
        obj["pocet_obyvatel"] = int(obyvatelstvo.query("vuzemi_kod==" + nuts_codes_citizen[kraj] +
                                    " & casref_do=='2020-12-31' & vek_kod.isnull() & pohlavi_kod.isnull()")["hodnota"].sum())
        obj["celkovy_pocet_nakazenych"] = len(
            osoby_nakazeni.query("kraj_nuts_kod=='" + kraj + "'"))
        obj["celkovy_pocet_ockovanych"] = int(osoby_ockovani.query(
            "kraj_nuts_kod == '" + kraj + "' & poradi_davky == 1")["pocet_davek"].sum())
        obj["vekove_skupiny"] = {}
        for skupina in vekove_skupiny:
            obj["vekove_skupiny"][skupina["nazev"]] = {
                "pocet_nakazenych": {
                    "muzi": len(osoby_nakazeni.query("kraj_nuts_kod == '" + kraj + "' & " + skupina["query"] + " & pohlavi == 'M'")),
                    "zeny": len(osoby_nakazeni.query("kraj_nuts_kod == '" + kraj + "' & " + skupina["query"] + " & pohlavi == 'Z'")),
                },
                "pocet_ockovanych": {
                    "muzi": int(osoby_ockovani.query("kraj_nuts_kod == '" + kraj + "' & poradi_davky == 1 & pohlavi == 'M' " + skupina["query_ockovani"])["pocet_davek"].sum()),
                    "zeny": int(osoby_ockovani.query("kraj_nuts_kod == '" + kraj + "' & poradi_davky == 1 & pohlavi == 'Z' " + skupina["query_ockovani"])["pocet_davek"].sum()),
                }
            }
        final_array.append(obj)

    # upload data to mongodb
    import_collection(db, COLLECTION_NAME, final_array)
