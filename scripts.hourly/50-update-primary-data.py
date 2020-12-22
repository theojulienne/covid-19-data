#!/usr/bin/env python3

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
    'United States Virgin Islands': 'Virgin Islands',
}

au_states_to_codes = {
    'New South Wales': 'NSW',
    'Victoria': 'VIC',
    'Queensland': 'QLD',
    'Western Australia': 'WA',
    'South Australia': 'SA',
    'Tasmania': 'TAS',
    'Australian Capital Territory': 'ACT',
    'Northern Territory': 'NT',

    'From Diamond Princess': 'From Diamond Princess',
}

all_states = {}
all_states.update(us_states_to_codes)
all_states.update(au_states_to_codes)
state_codes_to_names = {v: k for k, v in all_states.items()}

global_dates = []
today = datetime.datetime.utcnow().date()
curr = datetime.date(2020, 1, 22)
while curr <= today + datetime.timedelta(days=1): # account for TZs ahead of Actions
    global_dates.append(str(curr))
    curr = curr + datetime.timedelta(days=1)

with open('data_collation/jhu-live.json', 'r') as f:
    live_jhu_data = json.load(f)

for dataset in ['Confirmed', 'Deaths', 'Recovered']:
    fn = 'time_series_covid19_{}_global.csv'.format(dataset.lower())
    data = requests.get('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/' + fn)
    reader = csv.reader(data.content.decode('utf-8-sig').splitlines())
    header = next(reader)

    dates = []
    first_date_field = None
    for i, k in enumerate(header):
        try:
            if len(k.split('/')[-1]) == 4:
                d = datetime.datetime.strptime(k, '%m/%d/%Y').date()
            else:
                d = datetime.datetime.strptime(k, '%m/%d/%y').date()
        except ValueError: # skip other columns
            continue
        dates.append(str(d))
        if first_date_field is None:
            first_date_field = i

    assert dates[0] == global_dates[0], "Primary dataset must start at the same date as expected"

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

        if state:
            live_sample = live_jhu_data.get(country_name, {}).get('subseries', {}).get(state, {}).get('live', None)
        else:
            live_sample = live_jhu_data.get(country_name, {}).get('live', None)

        if country_code == 'USA':
            # don't use JHU live data for states, it doesn't agree with covidtracking and makes for confusing changes.
            live_sample = None

            # in the US, we need some special cases.
            # if we have city/county + state, exclude this for now. we could later include it as a subseries (otherwise we double count)
            if ', ' in state: continue

            # states must map to our list (and become codes)
            try:
                state = us_states_to_codes[state]
            except KeyError:
                print('WARNING: State name "{}" could not be found, skipping.'.format(state))
                continue
        elif country_code == 'AUS':
            state = au_states_to_codes[state]

        timeseries = []
        last = 0
        for d in row[first_date_field:]:
            if d == '':
                d = last
            else:
                d = int(d)
            timeseries.append(d)
            last = d

        if live_sample is not None:
            live_date = live_sample['date']
            if global_dates.index(live_date) == len(timeseries) and live_sample.get(dataset.lower()) > timeseries[-1]:
                # we have a live sample that is the "next day from where we have data"
                timeseries.append(live_sample[dataset.lower()])

        # skip country if it wasn't in latest dataset
        if dataset == 'Recovered' and country_code not in datasets: continue
        if state == '':
            datasets[country_code]['total'][dataset.lower()] = timeseries
        else:
            if dataset == 'Recovered' and state not in datasets[country_code]['subseries']: continue
            datasets[country_code]['subseries'][state]['total'][dataset.lower()] = timeseries

def cumulative_timeseries_add(a, b):
    new_a = a[:]
    new_b = b[:]

    # extend the smaller one to be as long as the longer one
    new_a += [a[-1]] * (len(new_b) - len(new_a))
    new_b += [b[-1]] * (len(new_a) - len(new_b))

    return list(map(lambda x, y: (x or 0) + (y or 0), new_a, new_b))

def subseries_total(part, pre_aggregated={}):
    totals = {}

    # find keys that are available in the totals for each subseries, those are what we can sum up
    keys_in_all = None
    for key, subseries in part['subseries'].items():
        if keys_in_all is None:
            keys_in_all = set(subseries['total'].keys())
        else:
            keys_in_all = keys_in_all & set(subseries['total'].keys())
    keys_in_all = keys_in_all | set(['confirmed', 'deaths', 'recovered'])

    for key, subseries in part['subseries'].items():
        for dataset, timeseries in subseries['total'].items(): # confirmed, deaths, recovered
            if dataset not in keys_in_all: continue # only aggregate data that all subseries have
            if dataset not in totals:
                totals[dataset] = timeseries
            else:
                totals[dataset] = cumulative_timeseries_add(totals[dataset], timeseries)

    # if we haven't aggregated ones we were provided externally, then use the aggregated numbers
    for key, value in pre_aggregated.items():
        if key not in totals:
            totals[key] = value

    return totals

# we now have datasets from the primary JHU source, let's overlay more up to date/detailed data from our other sources.
def merge_dataset(original_dates, original, updated, country_code, state_code):
    updated_dataset_dates = updated['timeseries_dates']
    del updated['timeseries_dates']

    updated_dataset_totals = updated['total']
    del updated['total']

    for series_name, series_data in updated_dataset_totals.items():
        # find the first not
        first_real_index = 0
        for i, val in enumerate(series_data):
            if val is not None and updated_dataset_dates[i] in original_dates: # keep skipping until we overlap with the main dataset
                # this is the first real datapoint, so start there
                first_real_index = i
                break
        first_new_date = updated_dataset_dates[first_real_index]
        # assert here that the overlayed updated dataset starts after the main one
        if first_new_date not in original_dates:
            print('WARNING: attempt to merge a dataset starting outside the original range {} in {} for {} in {}'.format(first_new_date, original_dates, state_code, country_code))
            return original

        date_index_in_old = original_dates.index(first_new_date)
        if series_name not in original['total']:
            # the main dataset doesn't have this. we just need to adjust the series to match dates
            updated_dataset_totals[series_name] = ([0] * date_index_in_old) + series_data[first_real_index:]
        else:
            # the main dataset DOES have this. what we want is all the data is had, before ours.
            # then, keep our data from then on.
            updated_dataset_totals[series_name] = original['total'][series_name][:date_index_in_old] + series_data[first_real_index:]

    # for i, date in enumerate(original_dates):
    #     print(i, date, updated_dataset_totals['confirmed'][i], original['total']['confirmed'][i])

    dataset = original.copy()
    for key,value in updated.items():
        if key not in original:
            # we need to deep find all subseries and pad them with empty data up until the start of the main dataset
            if isinstance(value, dict) and 'subseries' in value:
                # we've created a new dataset, so we use the first date and pad
                first_new_date = updated_dataset_dates[0]
                date_index_in_old = original_dates.index(first_new_date)
                for subseries_key, timeseries in value['subseries'].items():
                    value['subseries'][subseries_key] = ([0] * date_index_in_old) + timeseries
            dataset[key] = value
        else:
            print('WARNING: attempt to merge datasets with conflicting field {}'.format(key))

    # add in live data to the end of this overwritten states, if needed
    if country_code != 'USA': # don't use live data for USA, covidtracking is already frequent and JHU counts differently leading to confusion
        live_sample = None
        country_name = country_code_to_name[country_code]
        if country_name:
            if state_code:
                if state_code in state_codes_to_names:
                    state_name = state_codes_to_names[state_code]
                    live_sample = live_jhu_data.get(country_name, {}).get('subseries', {}).get(state_name, {}).get('live', None)
            else:
                live_sample = live_jhu_data.get(country_name, {}).get('live', None)
            if live_sample:
                live_date = live_sample['date']
                for key, timeseries in updated_dataset_totals.items():
                    if key not in live_sample: continue
                    if global_dates.index(live_date) == len(timeseries) and live_sample.get(key) > last_set_timeseries_value(timeseries):
                        # we have a live sample that is the "next day from where we have data"
                        timeseries.append(live_sample[key])

    # these have been combined, so let's overwrite them that way
    dataset['total'].update(updated_dataset_totals)

    return dataset

def last_set_timeseries_value(timeseries):
    for entry in reversed(timeseries):
        if entry is not None:
            return entry

for country_code in os.listdir('data_collation/by_state'):
    if os.path.isdir(os.path.join('data_collation/by_state', country_code)):
        for state_fn in os.listdir('data_collation/by_state/'+country_code):
            state_code, _ = state_fn.split('.')

            with open('data_collation/by_state/{}/{}.json'.format(country_code, state_code), 'r') as f:
                state_json = json.load(f)

            datasets[country_code]['subseries'][state_code] = merge_dataset(global_dates, datasets[country_code]['subseries'][state_code], state_json, country_code=country_code, state_code=state_code)
    else:
        # Strip the `.json` from the country code
        country_code = country_code.split('.')[0]
        with open('data_collation/by_state/{}.json'.format(country_code), 'r') as f:
            country_json = json.load(f)

        datasets[country_code] = merge_dataset(global_dates, datasets[country_code], country_json, country_code=country_code, state_code=None)

out = {
    'subseries': datasets,
    'timeseries_dates': global_dates,
}

# collate subseries into totals
for key, country_data in out['subseries'].items():
    if 'total' in country_data and 'confirmed' in country_data['total']: continue
    out['subseries'][key]['total'] = subseries_total(country_data, out['subseries'][key]['total'])
out['total'] = subseries_total(out)

def write_dataset(filename, dataset_name, dataset, cb_json={}):
    with open(filename + '.json', 'w') as o:
        json.dump(dataset, o, indent='  ', sort_keys=True)

    with open(filename + '.js', 'w') as o:
        o.write('var {} = '.format(dataset_name))
        json.dump(dataset, o, indent='  ', sort_keys=True)
        o.write(';\n')
        o.write('if (covid19_dataset_callback) covid19_dataset_callback(\'{}\', {}, {});\n'.format(dataset_name, dataset_name, json.dumps(cb_json)))

write_dataset('dataset', 'covid19_dataset', out)

if not os.path.exists('by_country'):
    os.makedirs('by_country')

for country_iso, dataset in out['subseries'].items():
    sub_dataset = {
        'timeseries_dates': global_dates,
    }
    sub_dataset.update(dataset)
    write_dataset('by_country/' + country_iso, 'covid19_dataset_country_' + country_iso.lower(), sub_dataset, {'country_iso': country_iso})

## make a top 10 countries file

def make_top10(dataset_name, field):
    country_totals = []

    for country_iso, dataset in out['subseries'].items():
        sort_value = dataset['total'][field][-1]
        country_totals.append((sort_value, country_iso))

    country_totals.sort()
    country_totals.reverse()

    top_10_subseries = {}

    for _, country_iso in country_totals[:10]:
        top_10_subseries[country_iso] = {
            'total': out['subseries'][country_iso]['total'], # we won't copy the subseries
        }

    top_10_dataset = {
        'subseries': top_10_subseries,
        'timeseries_dates': global_dates,
    }

    write_dataset(dataset_name, 'covid19_' + dataset_name, top_10_dataset)

make_top10('dataset_top10', 'confirmed')
make_top10('dataset_top10_by_deaths', 'deaths')

# world totals (no subseries)
world_summary = {
    'total': out['total'],
    'timeseries_dates': global_dates,
}
write_dataset('dataset_world_totals', 'covid19_dataset_world_totals', world_summary)
