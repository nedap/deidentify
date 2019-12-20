lint:
	pylint --disable=R,C deidentify scripts

lintall:
	pylint deidentify scripts

lintci:
	pylint --disable=R,C,W deidentify scripts || (echo "lintci failed with $$?"; exit 1)

test:
	pytest --doctest-modules --cov-report html --cov=deidentify deidentify/ tests/

publish:
	pip install --upgrade setuptools wheel twine
	python setup.py verify
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg deidentify.egg-info
