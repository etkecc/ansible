help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

pull-dependencies: ## Initializes this by pulling dependencies
	git submodule update --init --recursive
	ansible-galaxy install -r requirements.yml -p galaxy-roles/