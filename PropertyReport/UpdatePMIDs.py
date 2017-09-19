import pandas as pd
import requests
import json
with open("../.settings.json", 'r') as settings:
    credentials = json.load(settings)
    socrata_username = credentials["Socrata_Username"]#SOCRATA USERNAME
    socrata_password = credentials["Socrata_Password"]#SOCRATA PASSWORD

new_properties = pd.read_csv("NewPropertiesId.csv")
url = "https://noaa-ocao.data.socrata.com/dataset/Master-PortfolioManager-Property-List/phzv-979t"
