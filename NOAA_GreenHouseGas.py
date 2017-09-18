from EnergyStarAPI import EnergyStarClient
import pandas as pd
import json
with open("settings.json", 'r') as settings:
    credentials = json.load(settings)
    username = credentials["ES_Username"]#ENERGYSTAR USERNAME
    password = credentials["ES_Password"]#ENERGYSTAR PASSWORD
    socrata_username = credentials["Socrata_Username"]#SOCRATA USERNAME
    socrata_password = credentials["Socrata_Password"]#SOCRATA PASSWORD

client = EnergyStarClient(username, password)

if __name__ == "__main__":
    year = 2015
    month = 1
    master = pd.read_csv("https://noaa-ocao.data.socrata.com/api/views/phzv-979t/rows.csv?accessType=DOWNLOAD", dtype={"PM ID":object,"Property ID":object})

    property_list = master[master["PM ID"].notnull()]
    for idx, row in property_list.iterrows():
        greenhousegas = client.get_metric(row["PM ID"],"totalGHGEmissions",year,month,1, metric_name="GHG")
        ghg_df = pd.DataFrame(greenhousegas)
