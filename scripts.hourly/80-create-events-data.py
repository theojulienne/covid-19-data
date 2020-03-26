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

events_dir = 'data_collation/events'
for country_file in os.listdir(events_dir):
    with open(os.path.join(events_dir, country_file), 'r') as f:
        country_events_data = json.load(f)

    if 'country' not in country_events_data: continue
    if country_file != country_events_data['country'] + '.json': continue

    country = country_events_data['country']
    del country_events_data['country']

    dataset['countries'][country] = country_events_data

write_dataset('dataset_world_events', 'covid19_dataset_world_events', dataset)
