#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

trap 'rm -r $DIR/lastnames.zip $DIR/tmp_lastnames' EXIT

source activate deidentify
# Required for XML parsing
pip install lxml

echo 'Fetch and process firstnames...'
python "$DIR"/firstnames.py

echo 'Fetch and process lastnames'
curl http://www.naamkunde.net/wp-content/uploads/oudedocumenten/fn10k_versie1.zip -o "$DIR"/lastnames.zip
unzip -o "$DIR"/lastnames.zip -d "$DIR"/tmp_lastnames
python lastnames.py "$DIR"/tmp_lastnames/fn_10kw.xml
