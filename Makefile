MODULE := bot
TAG := $(shell git describe --tags --always)

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@echo 'Module:      '${MODULE}
	@echo 'Tag:         '${TAG}

configure:
	@pip install -r requirements.txt
	@./scripts/configure.sh

run:
	@python ${MODULE}/${MODULE}.py
