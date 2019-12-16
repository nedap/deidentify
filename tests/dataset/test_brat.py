from os.path import join, dirname
from deidentify.dataset import brat

def test_load_brat_config():
    config_file = join(dirname(__file__), 'test_config.conf')

    config = brat.load_brat_config(config_file)
    assert list(config.keys()) == ['entities']
    assert config['entities'] == ['Name', 'Initials', 'Profession', 'Hospital', 'Care_Institute', 'Organization_Company', 'Address', 'Internal_Location', 'Age', 'Date', 'Phone_fax', 'Email', 'URL_IP', 'SSN', 'ID', 'Other']
