import os
import loadpartialgtfs
from django.core.management.base import BaseCommand


IMPORT_GTFS_HELP = 'Import all the gtfs data from the specified directories'


class Command(BaseCommand):
    args = 'dir'
    help = IMPORT_GTFS_HELP

    def handle(self, *args, **options):
        # create different process for each parser in
        # order to reduce memory consumption
        root_dir = args[0]
        for parser_id in loadpartialgtfs.PARSER_CLASSES:
            # cmd = 'python manage.py loadpartialgtfs %s %s' % (root_dir, parser_id)
            cmd = 'python -m memory_profiler manage.py loadpartialgtfs %s %s' \
                  % (root_dir, parser_id)

            os.system(cmd)