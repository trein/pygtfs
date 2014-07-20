#!/usr/bin/env bash

# Setup Postgres/PostGIS
createuser root
dropdb pygtfs
createdb -T template_postgis pygtfs

# Load database

python manage.py syncdb
python manage.py loaddata ./extras/db/seed.json
python manage.py loadgtfs ./extras/data/br-poa

# Memory profiling
# python -m memory_profiler manage.py loadgtfs ./extras/data/br-poa

# Reset database
# python manage.py sqlclear service | python manage.py dbshell