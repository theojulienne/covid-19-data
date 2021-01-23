#!/usr/bin/env python3

import requests, json, os

country_specific_repos = {
  'AUS': {
    'repo': 'theojulienne/covid-19-data-aus',
    'states': ['ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA'],
    'events': True,
  },
  #'NZL': {
  #  'repo': 'tetrakai/covid-19-data-nz',
  #  'events': True,
  #},
  'USA': {
    'repo': 'theojulienne/covid-19-data-usa',
    'states': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'],
  },
  'ITA': {
    'repo': 'theojulienne/covid-19-data-ita',
    'states': [],
    'events': True,
  },
  'CHN': {
    'repo': 'theojulienne/covid-19-data-chn',
    'states': [],
    'events': True,
  }
}

for country_iso, config in country_specific_repos.items():
  if 'states' in config:
    for state_code in config['states']:
      url = 'https://raw.githubusercontent.com/{}/master/by_state/{}.json'.format(config['repo'], state_code.lower())
      response = requests.get(url)

      if response:
        state_data = response.json()
        country_dir = 'data_collation/by_state/{}'.format(country_iso)
        if not os.path.exists(country_dir):
          os.makedirs(country_dir)
        for skip in config.get('skip_totals', []):
          if skip in state_data['total']:
            del state_data['total'][skip]
        with open(os.path.join(country_dir, state_code+'.json'), 'w') as f:
          json.dump(state_data, f, indent=2, sort_keys=True)
      else:
        print('WARNING: could not retrieve expected {}'.format(url))

  # Not all countries have states!
  else:
    url = 'https://raw.githubusercontent.com/{}/master/{}.json'.format(config['repo'], country_iso.lower())
    response = requests.get(url)

    if response:
      country_data = response.json()

      for skip in config.get('skip_totals', []):
        if skip in country_data['total']:
          del country_data['total'][skip]

      with open(os.path.join('data_collation/by_state/{}.json'.format(country_iso)), 'w') as f:
        json.dump(country_data, f, indent=2, sort_keys=True)

    else:
      print('WARNING: could not retrieve expected {}'.format(url))

  if config.get('events', False):
    url = 'https://raw.githubusercontent.com/{}/master/events.json'.format(config['repo'])
    response = requests.get(url)

    if response:
      events_data = response.json()
      events_fn = 'data_collation/events/{}.json'.format(country_iso)
      with open(events_fn, 'w') as f:
        json.dump(events_data, f, indent=2, sort_keys=True)
    else:
      print('WARNING: could not retrieve expected {}'.format(url))
