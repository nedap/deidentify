"""
Parses XML of 10,000 most common lastnames fetched from Meertens Instituut.

See:
http://www.naamkunde.net/?page_id=294
"""
import sys
import xml.etree.ElementTree as ET
from os.path import dirname, join

import pandas as pd

OUT_PATH = dirname(__file__)

if __name__ == '__main__':
    lastnames_xml = sys.argv[1]
    root = ET.parse(lastnames_xml).getroot()

    names = []
    for name in root.findall('record'):
        names.append((
            name.find('prefix').text,
            name.find('naam').text
        ))

    names_df = pd.DataFrame(names, columns=['prefix', 'name'])
    names_df.to_csv(join(OUT_PATH, 'lastnames.csv'), index=False)
