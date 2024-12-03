PLANTUML = java -jar ~/plantuml.jar

.PHONY: all
all: check-style fix-style check-type run-test create-uml
	@echo "All done"

.PHONY: create-uml
create-uml:
ifeq ($(shell which java), )
	$(error "No java found in $(PATH). Install java to run plantuml")
endif
ifeq ($(wildcard ~/plantuml.jar), )
	@echo "Downloading plantuml.jar in home folder..."
	curl -L -o ~/plantuml.jar https://sourceforge.net/projects/plantuml/files/plantuml.jar/download
endif
	$(PLANTUML) umls/context.plantuml
	$(PLANTUML) umls/development.plantuml
	$(PLANTUML) umls/logical.plantuml
	$(PLANTUML) umls/physical.plantuml
	$(PLANTUML) umls/process.plantuml
	$(PLANTUML) umls/logic.plantuml
	$(PLANTUML) umls/bank_system.plantuml
	$(PLANTUML) umls/user_auth.plantuml
	$(PLANTUML) umls/bank_app.plantuml
	$(PLANTUML) umls/command.plantuml
	@echo "UML diagrams created and saved in umls folder"

.PHONY: build_db
build-db:
	@cd database && python3 setup_db.py && python3 -m database.init_db
# if you get a Makefile error just run ```python3 -m database.init_db``` by itself

.PHONY: run
run:
	@cd logic && export FLASK_APP=main:app && export PYTHONPATH=.. && flask run --debug

.PHONY: test
run-test:
	@echo "run pytest verbose"
	@pytest --verbose --color=yes --cov --cov-report term --cov-report html tests/
	@echo "Success"

.PHONY: clean
clean:
	@echo "Cleaning dirs"
	@rm -rf `find . -type d -name __pycache__`
	@rm -rf `find . -type d -name .pytest_cache`
	@rm -rf `find . -type d -name .mypy_cache`
	@rm -rf `*.pyc`
	@echo "Success"

.PHONY: check-style
check-style: 
	@echo "Checking style with flake8"
	@flake8 .
	@echo "Success"

.PHONY: fix-style
fix-style:
	autopep8 --in-place --recursive --aggressive --aggressive .

.PHONY: check-type
check-type:
	@echo "Checking type with mypy"
	@mypy --disallow-untyped-defs --strict .
	@echo "Success"