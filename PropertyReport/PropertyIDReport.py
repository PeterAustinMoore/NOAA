import sys
import os
path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)
from EnergyStarAPI import EnergyStarClient
import pandas as pd
import requests
import json
with open("../.settings.json", 'r') as f:
    settings = json.load(f)
    username = settings["ES_Username"]#ENERGYSTAR USERNAME
    password = settings["ES_Password"]#ENERGYSTAR PASSWORD
    socrata_username = settings["Socrata_Username"]#SOCRATA USERNAME
    socrata_password = settings["Socrata_Password"]#SOCRATA PASSWORD
    table_of_contents = settings["Table_of_Contents"]
client = EnergyStarClient(username, password)

if __name__ == "__main__":
    RPMD_DATA = "Properties.xls"
    rpmd = pd.read_excel(RPMD_DATA)
    lookup = pd.read_csv(table_of_contents)

    account_info = client.get_account_info()
    energystar_property_list = client.get_propery_list(account_info["account"]["id"]["$"])
    property_list = pd.DataFrame(energystar_property_list)
    property_list.columns = ["PM ID", "Property Name"]
    property_list.to_csv("CurrentEnergyStarProperties.csv", index=False)

    # Remove First and Last Rows
    rpmd = rpmd[1:]
    rpmd = rpmd[:-1]

    # Overwrite the Current Sites dataset on Socrata
    rpmd_url = "https://noaa-ocao.data.socrata.com/resource/8wgy-ye8p.json"
    response = requests.post(rpmd_url, data=rpmd.to_json(orient="records"), auth=(socrata_username, socrata_password))
    print(response.json())

    # Delineate the rpmd and lookup files
    lookup["FILE"] = "LOOKUP"
    rpmd["FILE"] = "RPMD"

    def ApplicableBuildings(row):
        if(row["Property Status"] != "Active"):
            return "N"
        if(row["Legal Interest"] == "Owned"):
            if(rpw["Complex Name"] != "DAVID SKAGGS RESEARCH CENTER"):
                return "GO"
        elif(row["Bureau/Line Office"] == "NWS"):
            return ""

    # Keep Certain Columns to Analyze
    lookup_cols_to_keep = ["FILE","PM ID","Property ID","Property Name","Property Type","Address","City","State","Zip"]
    rpmd_cols_to_keep = ["FILE","Property ID","Property Name","Property Type","Address","City","State","Zip"]

    lookup = lookup[lookup_cols_to_keep]
    rpmd = rpmd[rpmd_cols_to_keep]

    # Concatenate DataFrames to make Removing Duplicates easier
    to_dedup = pd.concat([lookup, rpmd])

    dedup = to_dedup.drop_duplicates(subset="Property ID", keep=False)
    dedup.to_csv("NewProperties.csv", index=False)
