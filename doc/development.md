# Development guide

## Install development repository
1. git clone this project
2. cd ansible-autodoc
3. `pip install -e ./`

## Test
Pytest are available in the tests folder, to run them execute `pytest` in the test directory

For more details check the pytest documentation

## Build and release

clean `./setup.py clean --all`

build `./setup.py sdist bdist_wheel`

upload `twine upload --repository-url https://pypi.org/legacy/ dist/*`