import pandas as pd

if __name__ == "__main__":
    RPMD_DATA = "Properties.xls"
    CURRENT_LOOKUP_TABLE = "https://noaa-ocao.data.socrata.com/api/views/phzv-979t/rows.csv?accessType=DOWNLOAD"
    rpmd = pd.read_excel(RPMD_DATA)
    rpmd["FILE"] = "RPMD"
    lookup = pd.read_csv(CURRENT_LOOKUP_TABLE)
    lookup["FILE"] = "LOOKUP"
    # Remove First and Last Rows
    rpmd = rpmd[1:]
    rpmd = rpmd[:-1]

    # Keep Certain Columns to Analyze
    lookup_cols_to_keep = ["FILE","PM ID","Property ID","Property Name","Property Type","Address","City","State","Zip"]
    rpmd_cols_to_keep = ["FILE","Property ID","Property Name","Property Type","Address","City","State","Zip"]

    lookup = lookup[lookup_cols_to_keep]
    rpmd = rpmd[rpmd_cols_to_keep]

    # Concatenate DataFrames to make Removing Duplicates easier
    to_dedup = pd.concat([lookup, rpmd])

    dedup = to_dedup.drop_duplicates(subset="Property ID", keep=False)
    dedup.to_csv("NewProperties.csv", index=False)
