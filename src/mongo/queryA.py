import collections
from pymongo import MongoClient
import pymongo, os, json, pandas
from pymongo.database import Database

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

def initialize_query_A():
    osoby_nakazeni = pandas.read_csv(os.path.join("data", "osoby.csv"))
    osoby_ockovani = pandas.read_csv(os.path.join("data", "ockovani-zakladni-prehled.csv"))

    kraje = osoby_nakazeni["kraj_nuts_kod"].unique()
    final_object = {}
    final_object["kraje"] = []

    for kraj in kraje:
        obj = {}
        obj["id"] = kraj
        obj["nazev_kraje"] = nuts_codes[kraj]
        obj["pocet_obyvatel"] = 5 #todo
        obj["celkovy_pocet_nakazenych"] = len(osoby_nakazeni.query("kraj_nuts_kod=='" + kraj + "'"))
        obj["celkovy_pocet_ockovanych"] = int(osoby_ockovani.query("kraj_nuts_kod == '" + kraj + "' & poradi_davky == 1")["pocet_davek"].sum())
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
        final_object["kraje"].append(obj)
    print(json.dumps(final_object, sort_keys=True, indent=4, ensure_ascii=False))