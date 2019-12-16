lint:
	pylint --disable=R,C deidentify scripts

lintall:
	pylint deidentify scripts

lintci:
	pylint --disable=R,C,W deidentify scripts || (echo "lintci failed with $$?"; exit 1)

test:
	pytest --doctest-modules --cov-report html --cov=deidentify deidentify/ tests/
