import requests, csv
from collections import defaultdict
import datetime
import json
import os

datasets = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

country_code_to_name = json.load(open('countries.json', 'r'))
country_name_to_code = {v: k for k, v in country_code_to_name.items()}

country_name_to_code.update({
    'Bosnia and Herzegovina': 'BIH',
    'Holy See': 'VAT',
    'Korea, South': 'KOR',
    'Cruise Ship': 'Cruise Ship',
    'Taiwan*': 'TWN',
    'United Kingdom': 'GBR',
    'Congo (Kinshasa)': 'COD',
    'Congo (Brazzaville)': 'COG',
    'Cote d\'Ivoire': 'CIV',
    'Antigua and Barbuda': 'ATG',
    'Trinidad and Tobago': 'TTO',
    'Saint Lucia': 'LCA',
    'Saint Vincent and the Grenadines': 'VCT',
    'Gambia, The': 'GMB',
    'Bahamas, The': 'BHS',
})

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
        country_name = row[country_field]
        state = row[state_field]

        # map the country to a country code
        country_code = country_name_to_code[country_name]
        
        timeseries = [int(p or '0') for p in row[first_date_field:]]

        if state == '':
            datasets[country_code]['total'][dataset.lower()] = timeseries
        else:
            datasets[country_code]['subseries'][state]['total'][dataset.lower()] = timeseries

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

def write_dataset(filename, dataset_name, dataset):
    with open(filename + '.json', 'w') as o:
        json.dump(dataset, o, indent='  ')

    with open(filename + '.js', 'w') as o:
        o.write('var ' + dataset_name + ' = ')
        json.dump(dataset, o, indent='  ')

write_dataset('dataset', 'covid19_dataset', out)

if not os.path.exists('by_country'):
    os.makedirs('by_country')

for country_iso, dataset in out['subseries'].items():
    write_dataset('by_country/' + country_iso, 'covid19_dataset_country_' + country_iso.lower(), dataset)
