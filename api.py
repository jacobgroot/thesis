"""
Thesis project 
Jacob Groot, 13174339
Universiteit van Amsterdam

HOW IT WORKS

With the code below, OECD rapports are downloaded. Not full rapports, only the GDP forecast data of 
the specified countries

OUTPUT:
data will be stored as csv file

HEADER:
title, year, country, GDP_t_min_2, GDP_t_min_1, GDP_t_plus_1, GDP_t_plus_2

EXPLANATION:
title of the rapport
year of the rapport
country of the forecast
The GDP as reported from 2 years before the rapport
The GDP as reported from 1 year before the rapport
The GDP as forecasted 1 year from the rapport
The GDP as forecasted 2 years from the rapport

with these forecasts and actual GDP's, we can compare the rapport to a rapport few years later to
see if it was accurate.

More countries can be added by adding country codes.
It does not go back further than 2010. API link fails after that. Reports are stored from there
on as flash files (?). Also variable names change. Because the variable names change, the API link
will need an update, but no way to be sure if it even supports an api call (it does not list it as
option on oecd.stat anymore) I have spent some time guessing links, unsuccessfully.

TODO:
- countries adding with sys.args
- put calling in main function 
- OOP?
- more rapports
- other source than OECD?
- statistical analysis
- visualisation

"""

import requests as rq
import csv
FILENAME = "data_gdp_forecast.csv"

def write_to_csv(data, filename):
    with open(filename, "a", newline="") as file:
        appender = csv.writer(file)
        appender.writerow(data)

def get_year(name):
    # year always follows the month
    month = set(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    name = name.split(" ")  
    for i, word in enumerate(name):
        if word in month:
            return name[i+1][:4]
        
    # return incase of failure
    return "No_year_found"

def get_json(rapport, country):
    try:
        json = rq.get(f"https://stats.oecd.org/SDMX-JSON/data/EO{rapport}_INTERNET/{country}.GDPV_ANNPCT.A/all?startTime=1995&endTime=2024&dimensionAtObservation=allDimensions", timeout=5)
    except rq.exceptions.Timeout:
        print(f"rapport {rapport} failed on timeout (5sec)")

    if json.status_code == 200:
        return json.json()
    else: 
        print("error: ", json.status_code)
        return 

def extract_data(json, name, year, country_name) : 
    data = [name, year, country_name]
    result = []
    for ob in json['dataSets'][0]['observations']:
        result.append(json['dataSets'][0]['observations'][ob][0])
    data.extend(result[-5:-3] + result[-2:])
    return data
        

# the rapports are numbered from 112 to 0, it works up until 88
previous_year = 113

# for now only download these countries
for country in ["NLD", "USA", "FRA", "DEU"]:
    for rapport in range(112, 87, -1):
        
        json = get_json(rapport, country)
        if not json:
            continue

        name = json['structure']['name']
        # horrendious data structure
        country_name = json['structure']['dimensions']['observation'][0]['values'][0]['name']

        year = get_year(name)
        if year == previous_year:
            continue

        data = extract_data(json, name, year, country_name)
    
        write_to_csv(data, FILENAME)
        previous_year = year