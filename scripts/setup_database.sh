#!/usr/bin/env bash

# Setup Postgres/PostGIS
createuser root
createdb -T template_postgis pygtfs

# Load database
python manage.py syncdb
python manage.py loaddata ./extras/db/seed.json
python manage.py loadgtfs ./extras/data/br-poa