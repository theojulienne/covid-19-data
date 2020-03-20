import requests, csv
from collections import defaultdict
import datetime
import json

def get_population():
    data = requests.get('https://github.com/datasets/population/raw/master/data/population.csv')
    reader = csv.reader(data.content.decode('utf-8').splitlines())
    header = next(reader)
    
    year_field = header.index('Year')
    country_field = header.index('Country Code')
    country_name_field = header.index('Country Name')
    value_field = header.index('Value')

    country_population = {}
    country_names = {}
    for row in reader:
        if row[year_field] != '2016': continue # latest available right now
        country = row[country_field]
        value = int(row[value_field])
        country_population[country] = value

        country_name = row[country_name_field]
        country_names[country] = country_name

    return country_population, country_names

out_pops, out_names = get_population()

with open('populations.json', 'w') as o:
    json.dump(out_pops, o, indent='  ')

with open('populations.js', 'w') as o:
    o.write('var covid19_dataset_populations = ')
    json.dump(out_pops, o, indent='  ')

with open('countries.json', 'w') as o:
    json.dump(out_names, o, indent='  ')

with open('countries.js', 'w') as o:
    o.write('var covid19_dataset_country_names = ')
    json.dump(out_names, o, indent='  ')