# NOAA EnergyStar Connector

## Getting Started
1. Install requirements

```
pip install -r requirements.txt
```

2. Add credentials

In the [settings.json](settings.json) file, add the Energystar username and password as well as Socrata username and password (for uploading). Optionally, keep the Socrata username and password None to write out the data to CSV.

3. Run the script

The script itself can be run or scripted simply as
```
python NOAA_EnergyStar.py
```

It will retrieve the the prior 3 month's worth data

## References

The script uses two datasets to collect data:
1. [The Master Portfolio Manager Dataset](https://noaa-ocao.data.socrata.com/d/phzv-979t) - Which contains the portfolio manager ID (PM ID) numbers for each property to collect usage and cost data for as well as the property ID number from RPMD which is used to join the data to the RPMD site information (#2)
2. [The RPMD Site Data](https://noaa-ocao.data.socrata.com/d/8wgy-ye8p) - Contains information pertaining to each site, such as area, address, bureau and other information. This is joined by Property ID field.


## Usage
The connector has one class:

1. EnergyStarClient

It is initiated by:
```python
from EnergyStarAPI import EnergyStarClient
ES_client = EnergyStarClient(username='myusername',password='mypassword')
```

## Responses

Successful EnergyStar API calls return XML responses that need to be parsed.

Errors are, unfortunately, not uniformly returned (either as HTML or XML). Therefore the full text of error response is returned at this time.

## Functions

	get_account_info()

Returns: account information (JSON)
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<account>
	<id>12341</id>
	<username>joebobonejob</username>
	<password>*********</password>
	<webserviceUser>true</webserviceUser>
	<searchable>true</searchable>
	<includeTestPropertiesInGraphics>true</includeTestPropertiesInGraphics>
	<contact>
		<address address1="2412 First St" address2="Apt 222" city="St Petersburg" state="FL" postalCode="61234" country="US"/>
		<email>temp@aol.com</email>
		<firstName>Joe</firstName>
		<phone>1234123412</phone>
		<lastName>Bob</lastName>
		<jobTitle>Data Analyst</jobTitle>
	</contact>
	<organization name="FirstAnalytics">
		<primaryBusiness>Data Center</primaryBusiness>
		<energyStarPartner>false</energyStarPartner>
	</organization>
	<securityAnswers/>
</account>
```


```python
get_building_info(prop_id)
```

Returns: building information (XML)
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<building>
	<name>1234 ABC Building</name>
	<address address1="1234 ABC St." city="Newark" state="NJ" postalCode="09231" county="Newark" country="US"/>
	<constructionStatus>Existing</constructionStatus>
	<primaryFunction>Data Center</primaryFunction>
	<yearBuilt>1910</yearBuilt>
	<grossFloorArea units="Square Feet" temporary="false" default="N/A"><value>4800</value></grossFloorArea>
	<occupancyPercentage>25</occupancyPercentage>
	<isFederalProperty>false</isFederalProperty>
	<accessLevel>Read</accessLevel>
	<audit>
		<createdBy>Joe</createdBy>
		<createdByAccountId>11111</createdByAccountId>
		<createdDate>2014-06-18T12:27:24.000-04:00</createdDate>
		<lastUpdatedBy>Joe</lastUpdatedBy>
		<lastUpdatedByAccountId>11111</lastUpdatedByAccountId>
		<lastUpdatedDate>2016-03-18T14:25:57.000-04:00</lastUpdatedDate>
	</audit>
</building>
```

```python
get_meter_list(prop_id)
```

Returns a dictionary of meters and their types associated with the property

```javascript
{123456:'Electric',4401234:'Natural Gas',1350101:'Municipally Supplied Potable Water - Mixed Indoor/Outdoor'}
```
```python
get_meter_type(meter_id)
```
Returns the type of meter

	'Electric' 'Natural Gas' 'Municipally Supplied Potable Water - Mixed Indoor/Outdoor' etc

```python
get_usage(meter_id, year, month, day)
```
Returns an array of monthly usage for the meter from the specified months ago

```javascript
[{'2016-03-31':102},{'2016-04-30':94.5}]
```
```python
get_cost(meter_id, year, month, day)
```
Returns an array monthly cost for the meter from the specified months ago

```javascript
[{'2016-03-31':23.5},{'2016-04-30':20.9}]
```
```python
get_usage_and_cost(meter_id, year, month, day)
```

Returns an array of monthly usage and cost from the specified months ago
```javascript
[{'2016-03-31':[102,23.5]},{'2016-04-30':[94.5,20.9]}]
```

```python
get_metric(property_id, metric, year=2015, month=1, day=1, metric_name="METRIC VALUE")
```
Returns an array of key (date) value, property ID, and value with "metric_name" as the key
```javascript
[{"PM ID":011102, "K":"07-01", "METRIC VALUE":14.2}]
```
