#!/bin/bash
# Fetches a list of countries and Dutch places.
#
# List of all countries with names and ISO 3166-1 codes
# Source: https://github.com/umpirsky/country-list
#
# List of Dutch places, zipcodes, streets
# Source: http://data.openov.nl/postcode-zones/

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

curl 'http://data.openov.nl/postcode-zones/postcodes-zones.csv.gz' > postcodes-zones.csv.gz
gunzip -f postcodes-zones.csv.gz

curl 'https://raw.githubusercontent.com/umpirsky/country-list/ad8f48405cc470d49dd535e2f2392e6572539d24/data/nl_NL/country.csv' > country.csv
