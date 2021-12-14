from mongo.mongo import initialize_mongo
from mongo.queryA import export_A_csvs
from csv_extractor.csvExtractor import convert_collection_to_csv


def main():
    """Extract needed CSV files from MONGO DB (for further diagrams plotting)
    """
    db = initialize_mongo()

    print("Extracting CSVs")
    export_A_csvs(db)
    convert_collection_to_csv("kraje_rok_mesiac",db)
    print("Export was succesfull, continue plotting with \"make plot\".")


if __name__ == '__main__':
    main()
