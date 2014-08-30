import os
from csv import DictReader
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from service import parsers
from collections import OrderedDict
from memory_profiler import profile

IMPORT_GTFS_HELP = 'Import all the gtfs data from the specified directories'
FINISHED = 'Loading finished at [%s]\n'
LOADED_DIRECTORY = 'Loaded directory [%s] at [%s]\n'
LOADING_DIRECTORY = 'Loading directory [%s]\n'
STARTING_LOADER = 'Starting loader at [%s]\n'
LOADING_FILE = 'Loading file [%s]'
LOADED_FROM = '[%s] loaded from [%s]\n'
STILL_IN_PROGRESS = '\tLoading [%s] lines from [%s], still in progress...\n'
WARNING_PROPERLY_NOT_LOADED = 'Warning file [%s] not found or ' \
                              'properly not loaded.\n'
ERROR_FILE_IS_REQUIRED = 'Could not load [%s] data properly, failed at line ' \
                         '[%s]. Fix the following problems, this file is ' \
                         'required: '

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
        self._log(STARTING_LOADER % str(datetime.now()))
        root_dir, parser_id = args

        self._log(LOADING_DIRECTORY % root_dir)
        parser_class = PARSER_CLASSES[parser_id]
        parser = parser_class()
        self._load(root_dir, parser)

        self._log(LOADED_DIRECTORY % (root_dir, str(datetime.now())))
        self._log(FINISHED % (str(datetime.now())))

    def _load(self, root_dir, parser):
        filename = parser.filename
        optional = parser.optional
        count = 0

        try:
            location = os.path.join(root_dir, filename)
            count = self._process_file(location, parser)
            self._log(LOADED_FROM % (count, filename))
        except parsers.ParserException as parser_error:
            raise CommandError(parser_error.message)
        except Exception as e:
            if not optional:
                raise CommandError(
                    ERROR_FILE_IS_REQUIRED % (filename, count) + str(e))
            else:
                self._log(WARNING_PROPERLY_NOT_LOADED % filename)

    def _process_file(self, location, parser):
        count = 0
        self._log(LOADING_FILE % location)
        with open(location, 'rb') as source:
            reader = DictReader(source)
            for line in reader:
                # parse line
                parser.parse(line)

                # provide feedback for long files
                count += 1
                if count % 10000 == 0:
                    self._log(STILL_IN_PROGRESS % (count, location))
        return count

    def _log(self, message):
        self.stdout.write(message)