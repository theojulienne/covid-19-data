var covid19_dataset_world_events = {
  "countries": {
    "AUS": {
      "events": [
        {
          "citations": [
            "https://www.theguardian.com/world/2020/mar/24/australias-coronavirus-self-isolation-rules-who-has-to-do-it-and-how-it-works"
          ],
          "control": {
            "class": "isolation",
            "type": "self-isolation"
          },
          "date": "2020-03-15",
          "name": "Australia institutes self-isolation rules for all incoming passengers",
          "type": "control"
        },
        {
          "citations": [
            "https://www.abc.net.au/news/2020-03-19/coronavirus-non-resident-travel-ban-australia/12071640"
          ],
          "control": {
            "class": "border-movement",
            "type": "non-citizen"
          },
          "date": "2020-03-20",
          "name": "Australia blocks arrival of all non-citizens, non-residents",
          "type": "control"
        },
        {
          "citations": [
            "https://www.theguardian.com/world/live/2020/mar/22/coronavirus-updates-live-australia-nsw-victoria-qld-tasmania-cases-government-stimulus-latest-update-news"
          ],
          "control": {
            "class": "resident-activity",
            "type": "lockdown"
          },
          "date": "2020-03-23",
          "name": "Australian non-essential services to close, schools stay open in stage one measures",
          "type": "control"
        }
      ]
    },
    "CHN": {
      "events": [
        {
          "citations": [
            "https://www.businessinsider.com.au/countries-on-lockdown-coronavirus-italy-2020-3?r=US&IR=T"
          ],
          "control": {
            "class": "resident-activity",
            "type": "lockdown"
          },
          "date": "2020-01-23",
          "name": "China places Wuhan into lockdown, followed by 15 other cities with infections",
          "type": "control"
        }
      ]
    },
    "ITA": {
      "events": [
        {
          "citations": [
            "https://www.bbc.com/news/world-europe-51810673",
            "https://en.wikipedia.org/wiki/2020_Italy_coronavirus_lockdown"
          ],
          "control": {
            "class": "resident-activity",
            "type": "lockdown"
          },
          "date": "2020-03-09",
          "name": "Italy extends emergency measures nationwide",
          "type": "control"
        }
      ]
    }
  }
};
if (covid19_dataset_callback) covid19_dataset_callback('covid19_dataset_world_events', covid19_dataset_world_events, {});
