#####
#
# Energy Star API
#
#####
import requests
import datetime
import logging
import xml.etree.ElementTree as Et
from xmljson import BadgerFish

class EnergyStarClient(object):
    def __init__(self, username, password, logging_level=logging.INFO):
        self.domain = "https://portfoliomanager.energystar.gov/ws"
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        logging.basicConfig(level=logging_level)
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.logger = logging.getLogger(__name__)

    def get_account_info(self):
        """
        Get Account information for the current user

        Returns:
            Dictionary : BadgerFish style representation of Energy Star response
                e.g.:
                account_info = client.get_account_info()
                account_id = account_info["account"]["id"]["$"]

        Notes:
            BadgerFish : http://www.sklar.com/badgerfish/
        """
        resource = self.domain + "/account"
        self.logger.debug("Pulling data from {0}".format(resource))
        response = self.session.get(resource)

        if response.status_code != requests.codes.ok:
            return response.raise_for_status()
        data = response.text
        root = Et.fromstring(data)
        bf = BadgerFish(dict_type=dict)
        account_info = bf.data(root)
        return account_info

    def get_propery_list(self, account_id):
        """
        Retrieve the properties associated with an account_id.
        NOTE: It appears the EnergyStar API does not return properties
        shared with you for some reason.
        Args:
            account_id : your account ID number, e.g. 100. Can be retrieved by
                        `client.get_account_info()["id"]`
        Returns:
            List of tuples : Array of tuples with property ID as the key and
                hint as the value, e.g. [(1,"Building 1"),(2, "Building 2")]

        Raises:
            HTTPError
        """
        resource = "{0}/account/{1}/property/list".format(self.domain, account_id)
        self.logger.debug("Pulling data from {0}".format(resource))
        response = self.session.get(resource)

        if response.status_code != requests.codes.ok:
            return response.raise_for_status()
        building_list = []
        root = Et.fromstring(response.text)
        for e in root.find("links"):
            data = (int(e.get("id")), e.get("hint"))
            building_list.append(data)
        return building_list

    def get_meter_list(self, prop_id):
        """
        Get a list of meters associated with a particular property

        Args:
            prop_id : the property id number

        Returns:
            List of Tuples : rray of tuples with Meter ID as the key and
                meter type as the value, e.g. [(1,"Electric - Grid"),(2, "Natural Gas")]

        Raises:
            HTTPError
        """

        resource =  '{0}/association/property/{1}/meter'.format(self.domain, prop_id)
        self.logger.debug("Pulling data from {0}".format(resource))
        response = self.session.get(resource)
        if(response.status_code != requests.codes.ok):
            return response.raise_for_status()
        meters = []
        root = Et.fromstring(response.text)
        for e in root.iter("*"):
            if e.tag == "meterId":
                meter_type = self.get_meter_type(e.text)
                data = (int(e.text), meter_type)
                meters.append(data)
        return meters


    def get_meter_type(self, meter_id):
        """
        Get the type of meter

        Args:
            meter_id : the id of the meter

        Returns:
            String : The type of meter, e.g. "Natural Gas"
        """
        resource = self.domain + '/meter/%s' % str(meter_id)
        self.logger.debug("Pulling data from {0}".format(resource))

        response = self.session.get(resource)
        if(response.status_code != requests.codes.ok):
            return response.raise_for_status()

        root = Et.fromstring(response.text)
        meter_type = ''
        for e in root.iter("*"):
            if e.tag == "type":
                meter_type = e.text

        return meter_type

    def get_building_info(self, prop_id):
        """
        Get the building info based on a property

        Args:
            prop_id : the property ID

        Returns:
            Dictionary : BadgerFish output of XML
        """
        resource = '{0}/building/{1}'.format(self.domain, prop_id)
        self.logger.debug("Pulling data from {0}".format(resource))
        response = self.session.get(resource)

        if response.status_code != requests.codes.ok:
            return response.raise_for_status()
        root = Et.fromstring(response.text)
        bf = BadgerFish(dict_type=dict)
        building_info = bf.data(root)
        return building_info

    def get_usage_data(self, meter_id, year=2015, month=1, day=1):
        """
        Get Usage Data

        Args:
            meter_id: the specific meter id
            year: start year, default 2015
            month: start month, default 1
            day: start day, default 1
        Returns:
            usage: Array of dictionaries {"DATE":YYYY-MM-DD, "USAGE":usage value}
        Notes:
            Meter IDs are returned from the get_meter_list function
        """
        # Get date in YYYY-MM-DD format from months ago
        date_format = '%Y-%m-%d'
        start_date = datetime.datetime(year, month, day)
        start_date_string = datetime.datetime.strftime(start_date, date_format)
        resource = '{0}/meter/{1}/consumptionData'.format(self.domain, meter_id)


        usage = []
        page = 1
        url = '{0}?page={1}&startDate={2}'.format(resource, page, start_date)

        while url:
            self.logger.debug("Pulling data from {0}".format(url))

            response = self.session.get(url)

            if response.status_code != requests.codes.ok:
                return response.raise_for_status()
            # Set URL to none to stop loop if no more links
            url = None

            root = Et.fromstring(response.text)
            for element in root.findall("meterConsumption"):
                month_data = dict()
                # Get the usage data
                month_data["DATE"] = element.find("endDate").text
                month_data["USAGE"] = float(element.find("usage").text)
                usage.append(month_data)


            # Get the next URL
            for element in root.find("links"):
                if element.get("linkDescription") == "next page":
                    url = self.domain + element.get("link")

        # Return the usage for the time period
        return usage

    def get_cost_data(self, meter_id, year=2015, month=1, day=1):
        """
        Get Cost Data

        Args:
            meter_id: the specific meter id
            year: start year, default 2015
            month: start month, default 1
            day: start day, default 1
        Returns:
            usage: Array of dictionaries {"DATE":YYYY-MM-DD, "COST":usage value}
        Notes:
            Meter IDs are returned from the get_meter_list function
        """
        # Get date in YYYY-MM-DD format from months ago
        date_format = '%Y-%m-%d'
        start_date = datetime.datetime(year, month, day)
        start_date_string = datetime.datetime.strftime(start_date, date_format)
        resource = self.domain + '/meter/%s/consumptionData' % str(meter_id)

        cost = []
        page = 1
        url = '{0}?page={1}&startDate={2}'.format(resource, page, start_date)

        while url:
            self.logger.debug("Pulling data from {0}".format(url))

            response = self.session.get(url, auth=(self.username, self.password))

            if response.status_code != requests.codes.ok:
                print(response.status_code, response.reason)
                break
            # Set URL to none to stop loop if no more links
            url = None

            root = Et.fromstring(response.text)
            for element in root.findall("meterConsumption"):
                month_data = dict()
                # Get the cost data
                month_data[element.find("endDate").text] = float(element.find("cost").text)
                # append to cost
                cost.append(month_data)

            # Get the next URL
            for element in root.find("links"):
                if element.get("linkDescription") == "next page":
                    url = self.domain + element.get("link")
        # Return the cost for the time period
        return cost

    def get_usage_and_cost(self, meter_id, year=2015, month=1, day=1):
        """
        Total Usage and Cost
        Args:
            meter_id: the specific meter id
            year: start year, default 2015
            month: start month, default 1
            day: start day, default 1
        Returns:
            usage_and_cost: Array of dictionaries
                {"DATE":"YYYY-MM-DD","USAGE":total monthly usage,"COST":total monthly cost}
        Notes:
            Meter IDs are returned from the get_meter_list function
        """
        date_format = '%Y-%m-%d'
        start_date = datetime.datetime(year, month, day)
        start_date_string = datetime.datetime.strftime(start_date, date_format)

        resource = '{0}/meter/{1}/consumptionData'.format(self.domain,meter_id)

        usage_and_cost = []
        page = 1
        # Initialize the URL
        url = '{0}?page={1}&startDate={2}'.format(resource, page, start_date_string)

        while url:
            self.logger.debug("Pulling data from {0}".format(url))
            page += 1

            response = self.session.get(url)

            if response.status_code != requests.codes.ok:
                return response.raise_for_status()

            # Set URL to none to stop loop if no more links
            url = None

            data = response.text
            root = Et.fromstring(data)
            for element in root.findall("meterConsumption"):
                month_data = dict()
                # Get the usage and cost data
                month_data["DATE"] = element.find("endDate").text
                month_data["USAGE"] = float(element.find("usage").text)
                try:
                    month_data["COST"] = float(element.find("cost").text)
                except AttributeError:
                    month_data["COST"] = 0

                # append to usage
                usage_and_cost.append(month_data)

            for element in root.findall("meterDelivery"):
                month_data = dict()
                # Get the usage and cost data
                month_data["DATE"] = element.find("deliveryDate").text
                month_data["USAGE"] = float(element.find("quantity").text)
                try:
                    month_data["COST"] = float(element.find("cost").text)
                except AttributeError:
                    month_data["COST"] = 0

                # append to usage
                usage_and_cost.append(month_data)
            # Get the next URL
            for element in root.find("links"):
                if element.get("linkDescription") == "next page":
                    url = "{0}{1}".format(self.domain, element.get("link"))
        # Return the cost for the time period
        return usage_and_cost

    def get_metric(self, property_id, metric, year=2015, month=1, day=1, metric_name="METRIC VALUE"):
        """
        PortfolioManager Specific Metric by Property
        Args:
            property_id: The specific property id
            metric: the portfolio manager metric (e.g. "GHG" or "GHG,Score")
                must be comma separated string.
            year: start year
            month: start month
            day: start day

        Returns:
            data: array of dictionaries {"DATE":"YYYY-MM", "PM ID":property_id, "METRIC VALUE":monthly value}
        """
        today = datetime.datetime.now()
        data = []
        dates = [(y, m) for y in range(year,today.year) for m in range(1,13)]
        dates.extend([(today.year, m) for m in range(1, month+1)])
        for year_month in dates:
            url = "{0}/property/{1}/metrics?year={2}&month={3}&measurementSystem=EPA".format(self.domain, property_id, year_month[0], year_month[1])
            self.logger.debug("Pulling data from {0}".format(url))
            if(year_month[1] < 10):
                date = "{0}-0{1}".format(year_month[0], year_month[1])
            else:
                date = "{0}-{1}".format(year_month[0], year_month[1])
            response = self.session.get(url, headers={"PM-Metrics":metric})
            if response.status_code != requests.codes.ok:
                return response.raise_for_status()
            root = Et.fromstring(response.text)
            for element in root.findall("metric"):
                d = {"PM ID":property_id, "K":date, metric_name:element.find("value").text}
                data.append(d)
        return data
