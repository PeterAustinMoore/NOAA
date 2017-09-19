import pandas as pd
import requests
import json
with open("../.settings.json", 'r') as d:
    settings = json.load(f)
    socrata_username = settings["Socrata_Username"]#SOCRATA USERNAME
    socrata_password = settings["Socrata_Password"]#SOCRATA PASSWORD
    table_of_contents = "https://noaa-ocao.data.socrata.com/resource/{0}.json".format(settings["Table_of_Contents"])

new_properties = pd.read_csv("NewProperties.csv")
new_properties = new_properties[["PM ID","Property ID","Category"]]

response = requests.post(table_of_contents, data=new_properties.to_json(orient="records"), auth=(socrata_username, socrata_password))
print(response.json())
