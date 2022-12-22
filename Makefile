MODULE := bot
TAG := $(shell git describe --tags --always)

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@echo 'Module:      '${MODULE}
	@echo 'Tag:         '${TAG}

configure:
	@pip install -r requirements.txt
	@python scripts/get_oauth_creds.py

run:
	@python ${MODULE}/${MODULE}.py
