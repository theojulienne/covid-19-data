#!/usr/bin/env python3

import os
import json

def write_dataset(filename, dataset_name, dataset, cb_json={}):
    with open(filename + '.json', 'w') as o:
        json.dump(dataset, o, indent='  ', sort_keys=True)

    with open(filename + '.js', 'w') as o:
        o.write('var {} = '.format(dataset_name))
        json.dump(dataset, o, indent='  ', sort_keys=True)
        o.write(';\n')
        o.write('if (covid19_dataset_callback) covid19_dataset_callback(\'{}\', {}, {});\n'.format(dataset_name, dataset_name, json.dumps(cb_json)))

dataset = {
  'countries': {}
}

with open('dataset.json', 'r') as f:
  full_dataset = json.load(f)

def latest_filled_value(ts):
  for v in reversed(ts):
    if v is not None:
      return v

def get_latest(series):
  return { k: latest_filled_value(v) for k,v in series['total'].items() }

for country_iso, country_data in full_dataset['subseries'].items():
  if country_iso not in dataset['countries']:
    dataset['countries'][country_iso] = {}
    if 'subseries' in country_data:
      dataset['countries'][country_iso]['states'] = {}
  
  dataset['countries'][country_iso]['latest'] = get_latest(country_data)
  for state_name, state_data in country_data.get('subseries', {}).items():
    dataset['countries'][country_iso]['states'][state_name] = get_latest(state_data)

write_dataset('dataset_latest_totals', 'covid19_dataset_latest_totals', dataset)
