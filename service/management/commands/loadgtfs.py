import os
from collections import OrderedDict
from django.core.management.base import BaseCommand
from service import parsers
from memory_profiler import profile

IMPORT_GTFS_HELP = 'Import all the gtfs data from the specified directories'

PARSER_CLASSES = OrderedDict([
    ('agency', parsers.AgencyParser),
    ('stops', parsers.StopsParser),
    ('routes', parsers.RoutesParser),
    ('shapes', parsers.ShapesParser),
    ('trips', parsers.TripsParser),
    ('stop_times', parsers.StopTimesParser),
    ('calendar', parsers.CalendarParser),
    ('calendar_dates', parsers.CalendarDatesParser),
])


class Command(BaseCommand):
    args = 'dir'
    help = IMPORT_GTFS_HELP

    @profile
    def handle(self, *args, **options):
        # create different process for each parser in
        # order to reduce memory consumption
        for parser_id in PARSER_CLASSES:
            root_dir = args[0]
            # cmd = 'python manage.py gtfsparser %s %s' % (root_dir, parser_id)
            cmd = 'python -m memory_profiler manage.py gtfsparser %s %s' % (
            root_dir, parser_id)
            os.system(cmd)
