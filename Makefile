PLANTUML = java -jar ~/plantuml.jar

.PHONY: all
all: create-uml
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

.PHONY: run
run:
	@cd logic && export FLASK_APP=main.py && flask run