.PHONY: help upstream roles dependencies versions commit-msg commit opml print-nofeeds

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

submodules: ## Initialize upstream with pinned commit
	git submodule update --init --recursive

roles: ## Pull roles
	ansible-galaxy install -r requirements.yml -p roles/galaxy/

dependencies: submodules roles ## Initializes this by pulling dependencies

versions: ## Update VERSIONS.md file using the actual versions from roles' files
	@bash bin/versions.sh
	@git --no-pager diff --no-ext-diff

commit: opml versions ## Make a commit
	git add --all
	git commit -S -q -m "$(shell bin/commit-msg.sh)"


opml: ## Dumps an OPML file with extracted git feeds for roles
	@python bin/feeds.py . dump

print-nofeeds: ## Prints roles files for which a GIT feeds couldn't be extracted
	@python bin/feeds.py . check
