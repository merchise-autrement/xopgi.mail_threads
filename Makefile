develop: setup-merchise-linter setup-git
	@echo ""


setup-merchise-linter:
	pip install --user git+git@gitlab.lahavane.com:support/merchise.lint.git#egg=merchise.lint-master

setup-git:
	@echo "--> Installing git hooks"
	git config branch.autosetuprebase always
	cd .git/hooks && ln -sf ../../hooks/* ./
	@echo ""
