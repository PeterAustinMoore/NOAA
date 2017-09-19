## Property Report

Objective:
- Read in current property information
- Update [RPMD dataset on Socrata](https://noaa-ocao.data.socrata.com/d/8wgy-ye8p)
- Determine duplicates with [The Master Portfolio Manager Dataset](https://noaa-ocao.data.socrata.com/d/phzv-979t) (i.e. properties that have not changed)
- Output a file with properties that need to be assigned Portfolio Manager IDs

### References
The PropertyIDReport.py script

### Input
[Properties.xls](Properties.xls)

### Output
CSV file of new properties as well as current properties that did not match.
[NewProperties.csv](NewProperties.csv)

CSV file with current energystar portfoliomanager properties and IDs
[CurrentEnergyStarProperties.csv](CurrentEnergyStarProperties.csv)
