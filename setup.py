import os
import sys

import setuptools
from setuptools.command.install import install

import deidentify

VERSION = deidentify.__version__

with open("README.md", "r") as fh:
    readme = fh.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches the version of the python package"""

    def run(self):
        tag = os.getenv('RELEASE_VERSION')

        if tag != VERSION:
            info = "Git tag: {} does not match the version of this package: {}".format(tag, VERSION)
            sys.exit(info)
        else:
            info = "Git tag: {} matches package version: {}".format(tag, VERSION)
            print(info)


setuptools.setup(
    name="deidentify",
    version=VERSION,
    author="Jan Trienes",
    author_email="jan.trienes@nedap.com",
    description="De-identify free-text medical records",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/nedap/deidentify",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    package_data={
        '': ['LICENSE'],
        'deidentify': [
            'surrogates/generators/resources/*.csv',
            'surrogates/generators/resources/*.txt'
        ]
    },
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests',
        'flair>=0.4.3',
        'torch>=1.1.0',
        'spacy>=2.2.1',
        'tqdm>=4.29',
        'deduce>=1.0.2',
        'loguru>=0.2.5',
        'sklearn-crfsuite>=0.3.6',
        'unidecode>=1.0.23',
        'pandas>=0.23.4',
        'nameparser>=1.0',
        'py-dateinfer>=0.4.5'
    ],
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
