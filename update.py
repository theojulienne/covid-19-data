import requests, csv
from collections import defaultdict
import datetime
import json

def get_population():
    data = requests.get('https://github.com/datasets/population/raw/master/data/population.csv')
    reader = csv.reader(data.content.decode('utf-8').splitlines())
    header = next(reader)
    
    year_field = header.index('Year')
    country_field = header.index('Country Name')
    value_field = header.index('Value')

    country_population = {}
    for row in reader:
        if row[year_field] != '2016': continue # latest available right now
        country = row[country_field]
        value = int(row[value_field])
        country_population[country] = value
        if country == 'United States':
            country_population['US'] = value
        elif country == 'Korea, Rep.':
            country_population['Korea, South'] = value

    return country_population

world_population = get_population()

datasets = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

for dataset in ['Confirmed', 'Deaths', 'Recovered']:
    data = requests.get('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-{}.csv'.format(dataset))
    reader = csv.reader(data.content.decode('utf-8').splitlines())
    header = next(reader)
    
    dates = []
    first_date_field = None
    for i, k in enumerate(header):
        try:
            d = datetime.datetime.strptime(k, '%m/%d/%y').date()
        except ValueError: # skip other columns
            continue
        dates.append(str(d))
        if first_date_field is None:
            first_date_field = i

    country_field = header.index('Country/Region')
    state_field = header.index('Province/State')

    for row in reader:
        country = row[country_field]
        state = row[state_field]
        
        timeseries = [int(p or '0') for p in row[first_date_field:]]

        if state == '':
            datasets[country]['total'][dataset.lower()] = timeseries
        else:
            datasets[country]['subseries'][state]['total'][dataset.lower()] = timeseries

for country, population in world_population.items():
    if country in datasets:
        datasets[country]['population'] = population

def subseries_total(part):
    totals = {}
    for key, subseries in part['subseries'].items():
        for dataset, timeseries in subseries['total'].items(): # confirmed, deaths, recovered
            if dataset not in totals:
                totals[dataset] = timeseries
            else:
                totals[dataset] = list(map(lambda a, b: a + b, totals[dataset], timeseries))
    return totals

out = {
    'subseries': datasets,
    'timeseries_dates': dates,
}

# collate subseries into totals
for key, country_data in out['subseries'].items():
    if 'total' in country_data: continue
    out['subseries'][key]['total'] = subseries_total(country_data)
out['total'] = subseries_total(out)

with open('dataset.json', 'w') as o:
    json.dump(out, o, indent='  ')

with open('dataset.js', 'w') as o:
    o.write('var covid19_dataset = ')
    json.dump(out, o, indent='  ')