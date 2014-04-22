from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from datetime import datetime
from service.parsers import *


IMPORT_GTFS_HELP = 'Import all the gtfs data from the specified directories'

FINISHED = 'Loading finished at %s\n'

LOADED_DIRECTORY = 'Loaded directory %s at %s\n'

LOADING_DIRECTORY = 'Loading directory %s\n'

STARTING_LOADER = 'Starting loader at %s\n'

LOADED_FROM = '%s loaded from %s\n'

STILL_IN_PROGRESS = '\tLoading %s lines from %s, still in progress...\n'

WARNING_PROPERLY_NOT_LOADED = 'Warning file %s not found or properly ' \
                              'not loaded.\n'

ERROR_FILE_IS_REQUIRED = 'Could not load %s data properly, failed at line ' \
                         '%s. Fix the following problems, this file is ' \
                         'required: '


class Command(BaseCommand):
    args = 'dir'
    help = IMPORT_GTFS_HELP

    def handle(self, *args, **options):
        self._log(STARTING_LOADER % str(datetime.now()))
        for root_dir in args:
            self._log(LOADING_DIRECTORY % root_dir)
            self._parse_data(root_dir)
            self._log(LOADED_DIRECTORY % (root_dir, str(datetime.now())))
        self._log(FINISHED % (str(datetime.now())))

    def _parse_data(self, root_dir):
        parsers = [
            AgencyParser(),
            StopsParser(),
            RoutesParser(),
            ShapesParser(),
            TripsParser(),
            StopTimesParser(),
            CalendarParser(),
            CalendarDatesParser(),
        ]

        for each in parsers:
            self._load(root_dir, each)

    def _process_file(self, root_dir, parser):
        count = 0
        filename = parser.filename
        reader = GtfsReader(root_dir, filename)

        for line in reader:
            (entity, created) = parser.parse(line)
            entity.save()

            # Provide feedback for long files
            count += 1
            if count % 10000 == 0:
                self._log(STILL_IN_PROGRESS % (count, filename))
        return count

    def _load(self, root_dir, parser):
        filename = parser.filename
        optional = parser.optional
        count = 0

        try:
            count = self._process_file(root_dir, parser)
            self._log(LOADED_FROM % (count, filename))
        except ParserException, parser_error:
            raise CommandError(parser_error.message)
        except Exception, e:
            if not optional:
                raise CommandError(ERROR_FILE_IS_REQUIRED
                                   % (filename, count) + str(e))
            else:
                self._log(WARNING_PROPERLY_NOT_LOADED % filename)

    def _log(self, message):
        self.stdout.write(message)