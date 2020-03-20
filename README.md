# covid19-data-js

The timeseries datasets from https://github.com/CSSEGISandData/COVID-19 converted into a JSON representation, and a JS file able to be included in other pages easily.

## Usage

Please use this URL to reference files here, since it's CDN fronted:
```html
<script src="https://theojulienne.github.io/covid-19-data/dataset.js"></script>
```

The data is available raw for downloading/polling (not too often!) from this CDN fronted URL:
```
https://theojulienne.github.io/covid-19-data/dataset.json
```

The full dataset will be available in the `covid19_dataset` variable, which looks like the following:
```js
{
  "timeseries_dates": ["2020-01-22", "2020-01-23", ..., today's date],
  "total": {
    "confirmed": [1, 2, 3, 4, ...],
    "deaths": [1, 2, 3, 4, ...],
    "recovered": [1, 2, 3, 4, ...],
  },
  "subseries": {
    "Australia": {
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

You can get a simple set of X/Y data for graphing software, with an X axis of `covid19_dataset['timeseries_dates']`, and Y axis of:
 * The world: `covid19_dataset['totals']['confirmed']`
 * A country: `covid19_dataset['subseries'][COUNTRY_NAME]['totals']['confirmed']`
 * A state/province: `covid19_dataset['subseries'][COUNTRY_NAME]['subseries'][STATE_NAME]['totals']['confirmed']`
