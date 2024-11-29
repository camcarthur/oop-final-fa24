PLANTUML = java -jar ~/plantuml.jar

.PHONY: all
all: create-uml run
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
	@echo "UML diagrams created and saved in umls folder"

.PHONY: build_db
build-db:
	@cd database && python3 setup_db.py && python3 -m database.init_db

.PHONY: run
run:
	@cd logic && export FLASK_APP=main:app && export PYTHONPATH=.. && flask run