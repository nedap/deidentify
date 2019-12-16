"""
Downloads list of 10,000 most common first names form Meertens Instituut website. Names are grouped
by female/male and will be written into separate files.

See:
http://www.naamkunde.net/?page_id=293
"""
from os.path import dirname, join

import pandas as pd

OUT_PATH = dirname(__file__)


def download_name_table(url, filename):
    names = pd.read_html(url, header=1)[0]
    names['Naam'] = names['Naam'].str.replace(r'\s\((V|M)\)', '')
    names[['Naam']].to_csv(join(OUT_PATH, filename), header=False, index=False)


if __name__ == '__main__':
    download_name_table('http://www.naamkunde.net/?page_id=293&vt_list_female=true',
                        'firstnames_female.txt')
    download_name_table('http://www.naamkunde.net/?page_id=293&vt_list_male=true',
                        'firstnames_male.txt')
