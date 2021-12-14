from mongo.mongo import initialize_mongo
from mongo.queryA import export_A_csvs


def main():
    """Extract needed CSV files from MONGO DB (for further diagrams plotting)
    """
    db = initialize_mongo()

    print("Extracting CSVs")
    export_A_csvs(db)
    # todo add CSVs for section B

    print("Export was succesfull, continue plotting with \"make plot\".")


if __name__ == '__main__':
    main()
