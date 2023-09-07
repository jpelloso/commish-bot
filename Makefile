MODULE := bot
TAG := $(shell git describe --tags --always)

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@echo 'Module:      '${MODULE}
	@echo 'Tag:         '${TAG}

configure:
	@pip3 install -r requirements.txt

run:
	@python3 ${MODULE}/${MODULE}.py
