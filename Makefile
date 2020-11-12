APP = /ella-admin

DJANGO_CONTAINER_NAME = django
DB_CONTAINER_NAME = ella-admin_postgresql_1

.PHONY: help Makefile

# Put it first so that "make" without argument is like "make help".
help:
	@echo "View the docs at: http://localhost:7000"
	@echo "View the Ella Web UI at : http://localhost:5001"
	@echo "View the Ella admin Django Interface at: http://localhost:8000"
	@echo "View JupyterLab at: http://localhost:8888"
	@echo "View Adminer at: http://localhost:8080"

build:
	docker-compose -f local.yml build

stop:
	docker-compose -f local.yml stop

dev:
	docker-compose -f local.yml up -d  --remove-orphans
	$(MAKE) help

wait:
	docker-compose -f local.yml exec ella-web \
		bash -c \
		"while ! pg_isready --host postgresql --dbname=postgres --username=ella; do sleep 5; done"

load:
	$(MAKE) wait
	@echo "Loading in database dump"
	docker-compose -f local.yml exec  \
		ella-web \
		bash -c "gunzip < /data/ella_db_1.sql.gz |PGPASSWORD=password123 psql -h postgresql -U postgres"

dump:
	$(MAKE) wait
	@echo "Loading in database dump"
	docker-compose -f local.yml exec  \
		postgresql \
		bash -c "PGPASSWORD=password123 pg_dump -h postgresql -U postgres postgres | gzip -9 > /data/ella_db_1.sql.gz"

db:
	$(MAKE) wait

	@echo "Creating database"
	docker-compose -f local.yml exec  \
		ella-web bash -c "ella-cli database make-production -f"

demo:
	$(MAKE) db
	@echo "Create HBOC v01 gene panel"
	docker-compose -f local.yml exec ella-web \
		bash -c \
		"ella-cli deposit genepanel --genepanel_name HBOC --genepanel_version v01 \
			--transcripts_path /ella/src/vardb/testdata/clinicalGenePanels/HBOC_v01/HBOC_v01.transcripts.csv \
			--phenotypes_path /ella/src/vardb/testdata/clinicalGenePanels/HBOC_v01/HBOC_v01.phenotypes.csv"

	@echo "Create HBOCUTV v01 gene panel"
	docker-compose -f local.yml exec  ella-web \
		bash -c \
		"ella-cli deposit genepanel --genepanel_name HBOCUTV --genepanel_version v01 \
			--transcripts_path /ella/src/vardb/testdata/clinicalGenePanels/HBOCUTV_v01/HBOCUTV_v01.transcripts.csv \
			--phenotypes_path /ella/src/vardb/testdata/clinicalGenePanels/HBOCUTV_v01/HBOCUTV_v01.phenotypes.csv"

	@echo "Create Mendeliome v01 gene panel"
	docker-compose -f local.yml exec  ella-web \
		bash -c \
		"ella-cli deposit genepanel --genepanel_name Mendeliome --genepanel_version v01 \
			--transcripts_path /ella/src/vardb/testdata/clinicalGenePanels/Mendeliome_v01/Mendeliome_v01.transcripts.csv \
			--phenotypes_path /ella/src/vardb/testdata/clinicalGenePanels/Mendeliome_v01/Mendeliome_v01.phenotypes.csv"

	@echo "Create Ciliopati v05 gene panel"
	docker-compose -f local.yml exec ella-web \
		bash -c \
		"ella-cli deposit genepanel --genepanel_name Ciliopati --genepanel_version v05 \
			--transcripts_path /ella/src/vardb/testdata/clinicalGenePanels/Ciliopati_v05/Ciliopati_v05.transcripts.csv \
			--phenotypes_path /ella/src/vardb/testdata/clinicalGenePanels/Ciliopati_v05/Ciliopati_v05.phenotypes.csv"

	@echo "Adding user groups"
	docker-compose -f local.yml exec \
		ella-web bash -c "ella-cli users add_groups /ella/src/vardb/testdata/usergroups.json"

	@echo "Adding users"
	docker-compose -f local.yml \
		exec ella-web bash -c "ella-cli users add_many /ella/src/vardb/testdata/users.json"

	@echo "Adding filter configs"
	docker-compose -f local.yml \
		exec ella-web bash -c "ella-cli filterconfigs update /ella/src/vardb/testdata/filterconfigs.json"

	@echo "Adding analyses"
	docker-compose -f local.yml \
		exec ella-web \
		bash -c "find /ella/src/vardb/testdata/analyses/default -name '*vcf' | grep -v Trio | grep -v brca_sample_2 | xargs -I {} ella-cli deposit analysis {}"

	# You may see an error like:
	# psycopg2.OperationalError: stack depth limit exceeded
    # HINT:  Increase the configuration parameter "max_stack_depth" (currently 2048kB), after ensuring the platform's stack depth limit is adequate.
    # This means that the machine you are on is not powerful enough to handle the database transaction
	@echo "Adding trio analyses"
	docker-compose -f local.yml \
		exec ella-web \
		bash -c "ella-cli deposit analysis \
			--ped /ella/src/vardb/testdata/analyses/default/HG002-Trio.Mendeliome_v01/HG002-Trio.Mendeliome_v01.ped
			/ella/src/vardb/testdata/analyses/default/HG002-Trio.Mendeliome_v01/HG002-Trio.Mendeliome_v01.vcf"

users_list:
	docker-compose -f local.yml exec ella-web \
		bash -c "ella-cli users list"

# Run as
# make ella_user=testuser1 user_reset_password
user_reset_password:
	docker-compose -f local.yml exec ella-web \
		bash -c "ella-cli users reset_password $(ella_user)"

clean:
	docker-compose -f local.yml stop; docker-compose -f local.yml rm -f -v

ella-web-logs:
	docker-compose -f local.yml logs ella-web

jupyter-token:
	docker-compose -f local.yml logs jupyter | grep 127 | grep token | tail -n 5

django-shell:
	docker exec -it $(DJANGO_CONTAINER_NAME) bash

migrate-django:
	docker exec -it $(DJANGO_CONTAINER_NAME) python manage.py migrate api
	docker-compose -f local.yml exec -T django python manage.py migrate django_cron
	docker-compose -f local.yml exec -T django python manage.py migrate sessions

make-migration-django:
	docker exec -it $(DJANGO_CONTAINER_NAME) python manage.py makemigrations

# It's temp
drop-db:
	docker kill $(DB_CONTAINER_NAME) && docker rm $(DB_CONTAINER_NAME)

db-shell:
	docker exec -it $(DB_CONTAINER_NAME) bash
