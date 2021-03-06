from EnergyStarAPI import EnergyStarClient
import pandas as pd
import datetime
from dateutil.relativedelta import *
import requests
import logging
import json
import xml.etree.ElementTree as Et
with open(".settings.json", 'r') as f:
    settings = json.load(f)
    username = settings["ES_Username"]#ENERGYSTAR USERNAME
    password = settings["ES_Password"]#ENERGYSTAR PASSWORD
    socrata_username = settings["Socrata_Username"]#SOCRATA USERNAME
    socrata_password = settings["Socrata_Password"]#SOCRATA PASSWORD

    socrata_dataset = "https://noaa-ocao.data.socrata.com/resource/{0}.json".format(settings["EnergyStarCostUsageDataset"])
    table_of_contents = "https://noaa-ocao.data.socrata.com/api/views/{0}/rows.csv?accessType=DOWNLOAD".format(settings["Table_of_Contents"])
    all_properties = "https://noaa-ocao.data.socrata.com/api/views/{0}/rows.csv?accessType=DOWNLOAD".format(settings["All_Properties"])

client = EnergyStarClient(username, password, logging_level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    # Set up relative time for automation
    today = datetime.datetime.now()
    start = today + relativedelta(months=-3)


    df_array = []
    logger.info("Reading in master table of contents...")
    master = pd.read_csv(table_of_contents, dtype={"PM ID":object,"Property ID":object})

    property_list = master[master["PM ID"].notnull()]

    logger.info("Reading in site lookup table...")
    sites = pd.read_csv(all_properties, dtype={"PM ID":object,"Property ID":object})

    ### PURE API
    # account_info = client.get_account_info()
    # p_list = client.get_propery_list(account_info["account"]["id"]["$"])

    for idx, row in property_list.iterrows():
        logger.info("Reading data for {0}:{1}".format(row["PM ID"], row["Property Name"]))
        # Filter out Property IDs
        if(row["Category"] == "N"):
            logger.debug("Passing {0}".format(row["PM ID"]))
            continue
        # Catch bad meter lists url
        logger.info("\tGetting Meter List...")
        try:
            meterlist = client.get_meter_list(row["PM ID"])
        except requests.exceptions.HTTPError as e:
            meterlist = []
        logger.info("\tRetrieved {0} Meter(s)".format(len(meterlist)))

        for meter in meterlist:
            # Catch bad meter URLs
            logger.info("\tReading data for {0}:{1}".format(meter[0], meter[1]))
            try:
                usage = client.get_usage_and_cost(meter[0], start.year, start.month, 1)
            except requests.exceptions.HTTPError:
                usage = []
            df = pd.DataFrame(usage)
            if(len(df) == 0):
                logger.info("Meter {0} on property {1} has no data".format(meter[1],row["Property Name"]))
                continue

            # Consistent information to all values
            df["PROPERTY"] = row["Property Name"]
            df["PROPERTY ID"] = row["Property ID"]
            df["PM ID"] = row["PM ID"]
            df["METER TYPE"] = meter[1]

            # Create the cost columns
            df_cost = df.pivot_table(index=["DATE","PM ID","PROPERTY","PROPERTY ID"], values=["COST"], columns=["METER TYPE"])
            df_cost.columns = df_cost.columns.get_level_values(1)
            df_cost.reset_index(inplace=True)
            df_cost["TOTAL COST"] = df_cost.sum(axis=1)

            # Create the usage columns
            df_usage = df.pivot_table(index=["DATE","PM ID","PROPERTY","PROPERTY ID"], values=["USAGE"], columns=["METER TYPE"])
            df_usage.columns = df_usage.columns.get_level_values(1)
            df_usage.reset_index(inplace=True)
            df_usage["TOTAL USAGE"] = df_usage.sum(axis=1)

            # Merge cost and usage columns, Create Fiscal Year and Fiscal Period from date column
            df_merged = df_cost.merge(df_usage, on=["DATE","PM ID","PROPERTY","PROPERTY ID"], suffixes=["_cost","_usage"])
            df_merged["METER TYPE"] = meter[1]
            df_merged["METER ID"] = meter[0]
            df_merged["FY"] = df_merged["DATE"].map(lambda x: x[0:4])
            df_merged["Fiscal Period"] = df_merged["DATE"].map(lambda x: x[5:7])
            df_merged["ROWID"] = df_merged["DATE"] + df_merged["METER ID"].astype(str)

            # Merge Property Data Information
            logger.info("\tMerging Property Information and Usage/Cost dataset")
            df_full = df_merged.merge(sites, left_on="PROPERTY ID", right_on="Property ID", how="inner")
            df_full["GHG"] = ""
            logger.info("\tMerged {0} row(s)".format(len(df_full)))
            if(socrata_username is not None):
                # Write to Socrata
                logger.info("Writing to Socrata...")
                response = requests.post(socrata_dataset, data=df_full.to_json(orient="records"),auth=(socrata_username, socrata_password))
                print(response.text)
            else:
                # Optional Write out to CSV
                logger.info("Writing to CSV...")
                df_full.to_csv("output.csv", index=False, na_rep="0", quoting=csv.QUOTE_ALL)
