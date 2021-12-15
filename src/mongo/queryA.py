import numpy as np
import matplotlib.pyplot as plt
import os
import pandas
from mongo.mongo import import_collection
from pymongo.database import Database

COLLECTION_NAME = "kraje_celkove"

CSV_FOLDER_NAME = "queries_csv"
DIAGRAMS_FOLDER_NAME = "img"

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
    osoby_ockovani = pandas.read_csv(os.path.join("data", "ockovani-zakladni-prehled.csv"))
    ockovani = pandas.read_csv(os.path.join("data", "ockovani.csv"))
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
        obj["pocet_obyvatel"] = int(obyvatelstvo.query("vuzemi_kod==" + nuts_codes_citizen[kraj] + " & casref_do=='2020-12-31' & vek_kod.isnull() & pohlavi_kod.isnull()")["hodnota"].sum())
        obj["celkovy_pocet_nakazenych"] = len(osoby_nakazeni.query("kraj_nuts_kod=='" + kraj + "'"))
        obj["celkovy_pocet_ockovanych"] = int(ockovani.query("kraj_nuts_kod == '" + kraj + "' & vakcina == 'Vaccine Janssen'")["prvnich_davek"].sum()) + \
            int(ockovani.query("kraj_nuts_kod == '" + kraj + "' & vakcina != 'Vaccine Janssen'")["druhych_davek"].sum())
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


def export_A_csvs(db: Database):
    # CSV for age distribution boxplot
    c = db["osoby"].find({})
    df = pandas.DataFrame(c)
    dff = df.drop(df.columns[[0, 2, 4, 6, 7, 8, 9]], axis=1)
    dff.to_csv(os.path.join(CSV_FOLDER_NAME, "queryA_1.csv"), index=False)

    # CSV for plotting vaccinated data
    o = db["ockovani-zakladni-prehled"].find({})
    osoby_ockovani = pandas.DataFrame(o)

    ids = []
    vaccinated_total = []
    vaccinated_man = []
    vaccinated_woman = []
    vaccinated_man_0_24 = []
    vaccinated_man_24_59 = []
    vaccinated_man_59_ = []
    vaccinated_woman_0_24 = []
    vaccinated_woman_24_59 = []
    vaccinated_woman_59_ = []

    for region in nuts_codes:
        unique_persons = osoby_ockovani.query("kraj_nuts_kod == '" + region + "' & ((vakcina == 'Vaccine Janssen' & poradi_davky == 1) | (vakcina != 'Vaccine Janssen' & poradi_davky == 2))")
        man = unique_persons.query("pohlavi == 'M'")
        woman = unique_persons.query("pohlavi == 'Z'")

        ids.append(region)
        vaccinated_total.append(int(unique_persons["pocet_davek"].sum()))
        vaccinated_man.append(int(man["pocet_davek"].sum()))
        vaccinated_woman.append(int(woman["pocet_davek"].sum()))
        vaccinated_man_0_24.append(int(man.query(
            "(vekova_skupina == '12-15' | vekova_skupina == '16-17' | vekova_skupina == '18-24')")["pocet_davek"].sum()))
        vaccinated_woman_0_24.append(int(woman.query(
            "(vekova_skupina == '12-15' | vekova_skupina == '16-17' | vekova_skupina == '18-24')")["pocet_davek"].sum()))
        vaccinated_man_24_59.append(int(man.query(
            "(vekova_skupina != '60-64' & vekova_skupina != '65-69' & vekova_skupina != '70-74' & vekova_skupina != '75-79' & vekova_skupina != '80+' & vekova_skupina != '12-15' & vekova_skupina != '16-17' & vekova_skupina != '18-24')")["pocet_davek"].sum()))
        vaccinated_woman_24_59.append(int(woman.query(
            "(vekova_skupina != '60-64' & vekova_skupina != '65-69' & vekova_skupina != '70-74' & vekova_skupina != '75-79' & vekova_skupina != '80+' & vekova_skupina != '12-15' & vekova_skupina != '16-17' & vekova_skupina != '18-24')")["pocet_davek"].sum()))
        vaccinated_man_59_.append(int(man.query(
            "(vekova_skupina == '60-64' | vekova_skupina == '65-69' | vekova_skupina == '70-74' | vekova_skupina == '75-79'| vekova_skupina == '80+')")["pocet_davek"].sum()))
        vaccinated_woman_59_.append(int(woman.query(
            "(vekova_skupina == '60-64' | vekova_skupina == '65-69' | vekova_skupina == '70-74' | vekova_skupina == '75-79'| vekova_skupina == '80+')")["pocet_davek"].sum()))

    df = pandas.DataFrame({
        "id": ids,
        "vaccinated_total": vaccinated_total,
        "vaccinated_men": vaccinated_man,
        "vaccinated_woman": vaccinated_woman,
        "vaccinated_men_0": vaccinated_man_0_24,
        "vaccinated_men_24": vaccinated_man_24_59,
        "vaccinated_men_59": vaccinated_man_59_,
        "vaccinated_woman_0": vaccinated_woman_0_24,
        "vaccinated_woman_24": vaccinated_woman_24_59,
        "vaccinated_woman_59": vaccinated_woman_59_,
    })
    df.to_csv(os.path.join(CSV_FOLDER_NAME, "queryA_2.csv"), index=False)

    # CSV for infected/vaccinated comparision
    col = db[COLLECTION_NAME]
    ids = []
    population = []
    infected = []
    vaccinated = []
    for obj in col.find({}):
        ids.append(obj["id"])
        population.append(obj["pocet_obyvatel"])
        infected.append(obj["celkovy_pocet_nakazenych"])
        vaccinated.append(obj["celkovy_pocet_ockovanych"])

    df_2 = pandas.DataFrame({
        "id": ids,
        "population": population,
        "infected": infected,
        "vaccinated": vaccinated,
    })
    df_2.to_csv(os.path.join(CSV_FOLDER_NAME, "query_comparision.csv"), index=False)


def plot_queries_A_boxplot():
    persons = pandas.read_csv(os.path.join(CSV_FOLDER_NAME, "queryA_1.csv"))

    fig = plt.figure(figsize=(13, 8))
    ax = fig.add_subplot(111)

    data = []
    for nuts_code in nuts_codes:
        region_persons = persons.query("kraj_nuts_kod == '" + nuts_code + "'")
        ages = region_persons["vek"]
        nd = np.array(ages)
        nd = nd[~np.isnan(nd)]
        data.append(nd)

    bp = ax.boxplot(data, patch_artist=True, notch='True', vert=0)

    ax.set_yticklabels(list(nuts_codes.values()))
    plt.xlabel('Věk', fontweight='bold', fontsize=12)

    plt.title("Rozložení věku nakažených osob v jednotlivých krajích ČR", fontweight='bold', fontsize=15)

    plt.savefig(os.path.join(DIAGRAMS_FOLDER_NAME, "queryA_1.png"))


def plot_queries_A_vaccinations_1():
    numbers = pandas.read_csv(os.path.join(CSV_FOLDER_NAME, "queryA_2.csv"))
    data = np.array(list(numbers["vaccinated_total"]))

    barWidth = 0.5
    fig = plt.subplots(figsize=(15, 8))

    br1 = np.arange(len(data))
    plt.barh(br1, data, color='b', height=barWidth, edgecolor='grey')
    plt.ticklabel_format(style='plain')

    plt.xlabel('Počet očkovaných', fontweight='bold', fontsize=12)
    plt.yticks([r for r in range(len(data))], list(nuts_codes.values()))

    plt.title("Počty provedených očkování v jednotlivých krajích na základě pohlaví", fontweight='bold', fontsize=15)

    plt.savefig(os.path.join(DIAGRAMS_FOLDER_NAME, "queryA_vaccinations_1.png"))


def plot_queries_A_vaccinations_2():
    numbers = pandas.read_csv(os.path.join(CSV_FOLDER_NAME, "queryA_2.csv"))
    data_men = np.array(list(numbers["vaccinated_men"]))
    data_women = np.array(list(numbers["vaccinated_woman"]))

    barWidth = 0.25
    fig = plt.subplots(figsize=(15, 8))

    br1 = np.arange(len(data_men))
    br2 = [x + barWidth for x in br1]

    plt.barh(br2, data_women, color='b', height=barWidth, edgecolor='grey', label='Muži')
    plt.barh(br1, data_men, color='r', height=barWidth, edgecolor='grey', label='Ženy')

    plt.xlabel('Počet očkovaných', fontweight='bold', fontsize=12)
    plt.yticks([r + barWidth for r in range(len(data_men))], list(nuts_codes.values()))

    plt.title("Počty provedených očkování v jednotlivých krajích na základě pohlaví", fontweight='bold', fontsize=15)
    plt.legend()

    plt.savefig(os.path.join(DIAGRAMS_FOLDER_NAME, "queryA_vaccinations_2.png"))


def plot_queries_A_vaccinations_3():
    numbers = pandas.read_csv(os.path.join(CSV_FOLDER_NAME, "queryA_2.csv"))
    data_men_0 = np.array(list(numbers["vaccinated_men_0"]))
    data_women_0 = np.array(list(numbers["vaccinated_woman_0"]))
    data_men_24 = np.array(list(numbers["vaccinated_men_24"]))
    data_women_24 = np.array(list(numbers["vaccinated_woman_24"]))
    data_men_59 = np.array(list(numbers["vaccinated_men_59"]))
    data_women_59 = np.array(list(numbers["vaccinated_woman_59"]))

    barWidth = 0.25
    fig = plt.subplots(figsize=(15, 8))

    br1 = np.arange(len(data_men_0))
    br2 = [x + barWidth for x in br1]

    plt.barh(br2, data_men_0, color='#0059ff', height=barWidth, edgecolor='grey', label='Muži 0-24')
    plt.barh(br2, data_men_24, left=data_men_0, color='#4788ff', height=barWidth, edgecolor='grey', label='Muži 24-59')
    plt.barh(br2, data_men_59, left=data_men_24, color='#9ec0ff', height=barWidth, edgecolor='grey', label='Muži 59+')
    plt.barh(br1, data_women_0, color='#ff0000',  height=barWidth, edgecolor='grey', label='Ženy 0-24')
    plt.barh(br1, data_women_24, color='#ff4f4f', left=data_women_0, height=barWidth, edgecolor='grey', label='Ženy 24-59')
    plt.barh(br1, data_women_59, color='#ff9999', left=data_women_24, height=barWidth, edgecolor='grey', label='Ženy 59+')

    plt.xlabel('Počet očkovaných', fontweight='bold', fontsize=12)
    plt.yticks([r + barWidth for r in range(len(data_men_0))], list(nuts_codes.values()))

    plt.title("Počty provedených očkování v jednotlivých krajích na základě pohlaví a věku", fontweight='bold', fontsize=15)
    plt.legend()

    plt.savefig(os.path.join(DIAGRAMS_FOLDER_NAME, "queryA_vaccinations_3.png"))


def plot_queries_comparision():
    def get_percentage(total, number):
        return (number / total) * 100
    numbers = pandas.read_csv(os.path.join(CSV_FOLDER_NAME, "query_comparision.csv"))
    percentage_vaccinated = []
    percentage_infected = []
    for i, row in numbers.iterrows():
        percentage_vaccinated.append(get_percentage(row["population"], row["vaccinated"]))
        percentage_infected.append(get_percentage(row["population"], row["infected"]))

    data_v = np.array(percentage_vaccinated)
    data_i = np.array(percentage_infected)

    barWidth = 0.25
    fig = plt.subplots(figsize=(15, 8))

    br1 = np.arange(len(data_i))
    br2 = [x + barWidth for x in br1]

    plt.barh(br2, data_i, color='r', height=barWidth, edgecolor='grey', label='Prodělané onemocnění')
    plt.barh(br1, data_v, color='g', height=barWidth, edgecolor='grey', label='Očkovaní')

    plt.xlabel('%', fontweight='bold', fontsize=12)
    plt.yticks([r + barWidth for r in range(len(data_i))], list(nuts_codes.values()))

    plt.title("Procentuální zastoupení očkovaných osob a osob s prodělaným onemocněním v jednotlivých krajích", fontweight='bold', fontsize=15)
    plt.legend()

    plt.savefig(os.path.join(DIAGRAMS_FOLDER_NAME, "query_comparision.png"))
