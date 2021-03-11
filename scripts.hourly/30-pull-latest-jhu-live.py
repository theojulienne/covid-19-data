#!/usr/bin/env python3

import requests, json, os
import datetime
from collections import defaultdict

feed_url = 'https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/1/query?f=json&where=Confirmed%3E0&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&outSR=102100&resultOffset=0&resultRecordCount=250&cacheHint=true'
feed_headers = { 'Referer': 'https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html' }

live_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))

response = requests.get(feed_url, headers=feed_headers)
if response:
  latest_date = None

  dataset_items = response.json()['features']
  for feature in dataset_items:
    point = feature['attributes']
    country = point['Country_Region']
    state = point['Province_State']
    live_data[country][state]['confirmed'] += point['Confirmed']
    if point['Recovered'] is not None:
        live_data[country][state]['recovered'] += point['Recovered']
    live_data[country][state]['deaths'] += point['Deaths']

    when = point['Last_Update'] / 1000.
    timestamp = datetime.datetime.utcfromtimestamp(when).date()
    if latest_date is None or timestamp > latest_date:
      latest_date = timestamp
    live_data[country][state]['date'] = str(timestamp)
  
  for country in live_data.keys():
    if None in live_data[country]:
      live_data[country] = {
        'live': live_data[country][None],
      }
    else:
      live_data[country] = {
        'subseries': { k: { 'live': v } for k,v in live_data[country].items() },
      }
    # print(country, live_data[country])

  live_fns = [
    'data_collation/jhu-live.json',
    # keep a daily archived copy as well
    'data_collation/jhu_live_cache/jhu-live-{}.json'.format(str(latest_date))
  ]
  for live_fn in live_fns:
    with open(live_fn, 'w') as f:
      json.dump(live_data, f, indent=2, sort_keys=True)
else:
  print("WARNING: Could not download latest live dataset", response)