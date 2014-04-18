from csv import DictReader
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from datetime import datetime
from service.parsers import *
import os


IMPORT_GTFS_HELP = "Import all the gtfs data from the specified directories"

FINISHED = "Loading finished at %s\n"

LOADED_DIRECTORY = "Loaded directory %s at %s\n"

LOADING_DIRECTORY = "Loading directory %s\n"

STARTING_LOADER = "Starting loader at %s\n"

LOADED_FROM = "%s loaded from %s\n"

STILL_IN_PROGRESS = "\tLoading %s lines from %s, still in progress...\n"

WARNING_PROPERLY_NOT_LOADED = "Warning file %s not found or properly " \
                              "not loaded.\n"

ERROR_FILE_IS_REQUIRED = "Could not load %s data properly, failed at line " \
                         "%s. Fix the following problems, this file is " \
                         "required: "


class Command(BaseCommand):
    args = 'dir'
    help = IMPORT_GTFS_HELP

    def handle(self, *args, **options):
        self.stdout.write(STARTING_LOADER % str(datetime.now()))
        for root_dir in args:
            self.stdout.write(LOADING_DIRECTORY % root_dir)
            self._parse_data(root_dir)
            self.stdout.write(LOADED_DIRECTORY
                              % (root_dir, str(datetime.now())))

        self.stdout.write(FINISHED % (str(datetime.now())))

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

    def _create_entity(self, line, parser):
        fields = parser.fields
        (entity, created) = parser.parse(line)

        for key, value in fields:
            field_data = check_field(line, value, optional=True)

            if not entity.__dict__[key] and field_data:
                entity.__dict__[key] = field_data
        entity.save()

    def _process_file(self, filename, parser, reader):
        count = 0
        for line in reader:
            self._create_entity(line, parser)

            # Provide feedback for long files
            count += 1
            if count % 10000 == 0:
                self.stdout.write(STILL_IN_PROGRESS % (count, filename))
        self.stdout.write(LOADED_FROM % (count, filename))
        return count

    def _load(self, root_dir, parser):
        filename = parser.filename
        optional = parser.optional
        count = 0

        try:
            reader = DictReader(open(os.path.join(root_dir, filename), 'rb'))
            count = self._process_file(filename, parser, reader)
        except ParserException, parser_error:
            raise CommandError(parser_error.message)
        except Exception, e:
            if not optional:
                raise CommandError(ERROR_FILE_IS_REQUIRED
                                   % (filename, count) + str(e))
            else:
                self.stdout.write(WARNING_PROPERLY_NOT_LOADED % filename)


