# covid-19-data

The timeseries datasets from https://github.com/CSSEGISandData/COVID-19 converted into a JSON representation, and a JS file able to be included in other pages easily.

## Direct sources for some countries

This repo collates multiple datasets into a single dataset used by [covid.graphics](https://covid.graphics). These specific datasets are:
 * Australia - https://github.com/theojulienne/covid-19-data-aus
 * United States - https://github.com/theojulienne/covid-19-data-usa

## Usage

Please use these URLs to reference files here, since it's CDN fronted:
```html
<script src="https://theojulienne.github.io/covid-19-data/dataset.js"></script>
<script src="https://theojulienne.github.io/covid-19-data/populations.js"></script>
<script src="https://theojulienne.github.io/covid-19-data/countries.js"></script>
```

The country data is also available on a single country basis:
```
<script src="https://theojulienne.github.io/covid-19-data/by_country/AUS.js"></script>
```

The data is available raw for downloading/polling (not too often!) from this CDN fronted URLs:
```
https://theojulienne.github.io/covid-19-data/dataset.json
https://theojulienne.github.io/covid-19-data/populations.json
https://theojulienne.github.io/covid-19-data/countries.json
```

Using the JS option, the full dataset will be available in the `covid19_dataset` variable. Either way, the JSON or variable looks like the following:
```js
{
  "timeseries_dates": ["2020-01-22", "2020-01-23", ..., today's date],
  "total": {
    "confirmed": [1, 2, 3, 4, ...],
    "deaths": [1, 2, 3, 4, ...],
    "recovered": [1, 2, 3, 4, ...],
  },
  "subseries": {
    "AUS": {
      "population": 24127159, # approximate, and only for some countries right now
      "total": {
        "confirmed": [1, 2, 3, 4, ...],
        "deaths": [1, 2, 3, 4, ...],
        "recovered": [1, 2, 3, 4, ...],
      },
      "subseries": {
        "New South Wales": {
          "total": {
            "confirmed": [1, 2, 3, 4, ...],
            "deaths": [1, 2, 3, 4, ...],
            "recovered": [1, 2, 3, 4, ...],
          },
        },
        ... more states ...
      },
    },
    ... more countries ...
  },
}
```

The `populations.js(on)` files contain the populations of countries by code. The variable in the `.js` version is `covid19_dataset_populations` and it maps a country code to a population.

The `countries.js(on)` files contain the names of countries by code, all codes are [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) where available. The variable in the `.js` version is `covid19_dataset_country_names` and it maps a country code to a country name.

For any of the covid19 timeseries `.js` files including `by_country/<COUNTRY_CODE>.js` files, if a function called `covid19_dataset_callback` exists, it will be called as follows to facilitate dynamic loading:
```
if (covid19_dataset_callback) covid19_dataset_callback('covid19_dataset_country_aus', covid19_dataset_country_aus, {"country_iso": "AUS"});
```

You can get a simple set of X/Y data for graphing software, with an X axis of `covid19_dataset['timeseries_dates']`, and Y axis of:
 * The world: `covid19_dataset['totals']['confirmed']`
 * A country: `covid19_dataset['subseries'][COUNTRY_CODE]['totals']['confirmed']`
 * A state/province: `covid19_dataset['subseries'][COUNTRY_CODE]['subseries'][STATE_NAME]['totals']['confirmed']`
