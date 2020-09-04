# Contributing

We are happy to incorporate any improvements to this package if you submit them as a pull request. To start development on this package, clone it to a location of your choice:

```sh
git clone https://github.com/nedap/deidentify.git
```

We use conda for dependency management:

```sh
# Install package dependencies and add local files to the Python path of that environment.
conda env create -f environment.yml
conda activate deidentify && export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Testing and Linting

Execute the following to add the development dependencies to this project:

```sh
pip install -U -r requirements-dev.txt
```

To run unit tests and code linting execute:

```sh
make test
make lint
```

## Release

To create a GitHub and PyPI release, use following command. You will be prompted for your [GitHub access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) and PyPI credentials.

```sh
./release.sh <version>
```
