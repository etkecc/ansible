.PHONY: help upstream roles dependencies

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

submodules: ## Initialize upstream with pinned commit
	git submodule update --init --recursive

roles: ## Pull roles
	ansible-galaxy install -r requirements.yml -p roles/galaxy/

dependencies: submodules roles ## Initializes this by pulling dependencies
