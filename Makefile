.PHONY: help upstream roles dependencies

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

submodules: ## Initialize upstream with pinned commit
	git submodule update --init --recursive

roles: ## Pull roles
	ansible-galaxy install -r requirements.yml -p roles/galaxy/

dependencies: submodules roles ## Initializes this by pulling dependencies

dump-roles-feeds: ## Dumps an OPML file with extracted git feeds for roles
	python bin/get-releases-feeds-for-roles.py $(PWD) dump

check-roles-feeds: ## Prints roles files for which a GIT feeds couldn't be extracted
	python bin/get-releases-feeds-for-roles.py $(PWD) check
