#!/usr/bin/env python3

import requests, json, os

country_specific_repos = {
  'AUS': {
    'repo': 'theojulienne/covid-19-data-aus',
    'states': ['NSW'],
  }
}

for country_iso, config in country_specific_repos.items():
  for state_code in config['states']:
    url = 'https://raw.githubusercontent.com/{}/master/by_state/{}.json'.format(config['repo'], state_code.lower())
    response = requests.get(url)
    
    if response:
      state_data = response.json()
      country_dir = 'data_collation/by_state/{}'.format(country_iso)
      if not os.path.exists(country_dir):
        os.makedirs(country_dir)
      with open(os.path.join(country_dir, state_code+'.json'), 'w') as f:
        json.dump(state_data, f, indent=2)
    else:
      print('WARNING: could not retrieve expected {}'.format(url))