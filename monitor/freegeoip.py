from urllib import urlopen
from csv import reader
import sys
import re
FREE_GEOIP_CSV_URL = "http://freegeoip.net/csv/%s"
def valid_ip(ip):

    pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

    return re.match(pattern, ip)

def __get_geodata_csv(ip):
    if not valid_ip(ip):
        raise Exception('Invalid IP format', 'You must enter a valid ip format: X.X.X.X')
    
    URL = FREE_GEOIP_CSV_URL % ip
    response_csv = reader(urlopen(URL))
    csv_data = response_csv.next()

    return {
        "status": u"True" == csv_data[0],
        "ip":csv_data[1],
        "countrycode":csv_data[2],
        "countryname":csv_data[3],
        "regioncode":csv_data[4],
        "regionname":csv_data[5],
        "city":csv_data[6],
        "zipcode":csv_data[7],
        "latitude":csv_data[8],
        "longitude":csv_data[9]
    }

def get_geodata(ip):
    return __get_geodata_csv(ip)

