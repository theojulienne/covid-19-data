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
    'Cabo Verde': 'CPV',
    'East Timor': 'TMP',
})

us_states_to_codes = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",

    'Diamond Princess': 'Diamond Princess',
    'Grand Princess': 'Grand Princess',
    'Puerto Rico': 'Puerto Rico',
    'Guam': 'Guam',
    'Virgin Islands': 'Virgin Islands',
}

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
        try:
            country_code = country_name_to_code[country_name]
        except KeyError:
            print('WARNING: Country name "{}" could not be found, skipping.'.format(country_name))
            continue

        if country_code == 'USA':
            # in the US, we need some special cases.
            # if we have city/county + state, exclude this for now. we could later include it as a subseries (otherwise we double count)
            if ', ' in state: continue

            # states must map to our list (and become codes)
            state = us_states_to_codes[state]
        
        timeseries = []
        last = 0
        for d in row[first_date_field:]:
            if d == '':
                d = last
            else:
                d = int(d)
            timeseries.append(d)
            last = d

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

def write_dataset(filename, dataset_name, dataset, cb_json={}):
    with open(filename + '.json', 'w') as o:
        json.dump(dataset, o, indent='  ')

    with open(filename + '.js', 'w') as o:
        o.write('var {} = '.format(dataset_name))
        json.dump(dataset, o, indent='  ')
        o.write(';\n')
        o.write('if (covid19_dataset_callback) covid19_dataset_callback(\'{}\', {}, {});\n'.format(dataset_name, dataset_name, json.dumps(cb_json)))

write_dataset('dataset', 'covid19_dataset', out)

if not os.path.exists('by_country'):
    os.makedirs('by_country')

for country_iso, dataset in out['subseries'].items():
    sub_dataset = {
        'timeseries_dates': dates,
    }
    sub_dataset.update(dataset)
    write_dataset('by_country/' + country_iso, 'covid19_dataset_country_' + country_iso.lower(), sub_dataset, {'country_iso': country_iso})

## make a top 10 countries file

country_totals = []

for country_iso, dataset in out['subseries'].items():
    latest_confirmed = dataset['total']['confirmed'][-1]

    country_totals.append((latest_confirmed, country_iso))

country_totals.sort()
country_totals.reverse()

top_10_subseries = {}

for _, country_iso in country_totals[:10]:
    top_10_subseries[country_iso] = {
        'total': out['subseries'][country_iso]['total'], # we won't copy the subseries
    }

top_10_dataset = {
    'subseries': top_10_subseries,
    'timeseries_dates': dates,
}

write_dataset('dataset_top10', 'covid19_dataset_top10', top_10_dataset)

# world totals (no subseries)
world_summary = {
    'total': out['total'],
    'timeseries_dates': dates,
}
write_dataset('dataset_world_totals', 'covid19_dataset_world_totals', world_summary)
