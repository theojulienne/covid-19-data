import requests, csv
from collections import defaultdict
import datetime
import json

def get_iso_codes():
    data = requests.get('https://github.com/datasets/country-codes/raw/master/data/country-codes.csv')
    reader = csv.reader(data.content.decode('utf-8').splitlines())
    header = next(reader)

    iso_field = header.index('ISO3166-1-Alpha-3')
    ioc_field = header.index('IOC')
    name_field = header.index('CLDR display name')

    ioc_to_iso = {}
    iso_to_name = {}
    for row in reader:
        c_iso = row[iso_field]
        c_ioc = row[ioc_field]
        c_name = row[name_field]

        ioc_to_iso[c_ioc] = c_iso
        iso_to_name[c_iso] = c_name
    
    # missing from this dataset
    iso_to_name['RKS'] = 'Kosovo'

    return ioc_to_iso, iso_to_name

ioc_to_iso, iso_to_name = get_iso_codes()

def get_population():
    data = requests.get('https://github.com/datasets/population/raw/master/data/population.csv')
    reader = csv.reader(data.content.decode('utf-8').splitlines())
    header = next(reader)
    
    year_field = header.index('Year')
    country_field = header.index('Country Code')
    country_name_field = header.index('Country Name')
    value_field = header.index('Value')

    population_best = defaultdict(lambda: 0)

    country_population = {}
    for row in reader:
        country = row[country_field]
        value = int(row[value_field])

        # if country not in ioc_to_iso: continue
        if country not in iso_to_name: continue

        # iso = ioc_to_iso[country]
        iso = country

        year = int(row[year_field])
        if year < population_best[country]:
            continue # our year is older than the one so far, ignore

        country_population[iso] = value

    return country_population

out_names = iso_to_name
out_pops = get_population()

with open('populations.json', 'w') as o:
    json.dump(out_pops, o, indent='  ', sort_keys=True)

with open('populations.js', 'w') as o:
    o.write('var covid19_dataset_populations = ')
    json.dump(out_pops, o, indent='  ', sort_keys=True)

with open('countries.json', 'w') as o:
    json.dump(out_names, o, indent='  ', sort_keys=True)

with open('countries.js', 'w') as o:
    o.write('var covid19_dataset_country_names = ')
    json.dump(out_names, o, indent='  ', sort_keys=True)