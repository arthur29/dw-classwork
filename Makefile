.PHONY: create migrate populate real_demand projected_demand lead_time security_level dam ressuply_level

## all: create and run all targets
all: populate real_demand projected_demand lead_time
## create: create the database
create:
	@python3 create.py
## migrate: create the tables in database
migrate: create
	@python3 migrate.py
## populate: read PRODUTO.csv and use it to populate tables
populate: migrate
	@python3 populate.py
## total_order: populate total_orders DW
total_order:
	@python3 total_order.py
## projected_demand: populate the projected_demand DW
projected_demand:
	@python3 projected_demand.py
## lead_time: populate lead_time column in InventoryControl DW
lead_time:
	@python3 lead_time.py
## security_level: populate security_level column in InventoryControl DW
security_level: lead_time
	@python3 security_level.py
## dam: populate the DAM column in InventoryControl DW
dam:
	@python3 DAM.py
## ressuply_level: populate the NRS in INventoryControl DW
ressuply_level:
	@python3 ressuply_level.py
## help: show this message
help:
	@echo "DW work:"
	@echo
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	@echo
