from csv import DictReader
from django.contrib.gis.geos import fromstr
from service.models import *
from datetime import time
from datetime import date
import os


class ParserException(Exception):
    @staticmethod
    def for_message(message):
        return ParserException(message)

    @staticmethod
    def for_args(*args):
        return ParserException(*args)


def check_field(reader, field, optional=False):
    if field in reader and reader[field]:
        return reader[field]
    elif not optional:
        raise ParserException.for_message(
            'Field %s was empty or non-present in file' % field)
    return None


class GtfsReader(object):
    def __init__(self, root_dir, filename):
        self.reader = DictReader(open(os.path.join(root_dir, filename), 'rb'))

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next()


class BaseParser(object):
    def __init__(self, filename, optional=False):
        self.filename = filename
        self.optional = optional

    @staticmethod
    def parse(line):
        raise ParserException('Parser methods not implemented.')

    @staticmethod
    def create_geopoint(lat, lng):
        return fromstr('POINT(%s %s)' % (float(lat), float(lng)))


class AgencyParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'agency.txt')

    @staticmethod
    def parse(line):
        name = check_field(line, 'agency_name')
        url = check_field(line, 'agency_url')
        a_timezone = check_field(line, 'agency_timezone')

        (entity, created) = Agency.objects.get_or_create(
            name=name, url=url, timezone=a_timezone)

        # Optional parameters
        entity.agency_id = check_field(line, 'agency_id', optional=True)
        entity.lang = check_field(line, 'agency_lang', optional=True)
        entity.phone = check_field(line, 'agency_phone', optional=True)
        entity.fare_url = check_field(line, 'agency_fare_url', optional=True)

        return entity, created


class CalendarParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'calendar.txt')

    @staticmethod
    def parse(line):
        temp = check_field(line, 'start_date')
        start_date = date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))

        temp = check_field(line, 'end_date')
        end_date = date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))

        try:
            service_id = check_field(line, 'service_id')
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist, e:
            raise ParserException.for_args(e.args)

        return Calendar.objects.get_or_create(
            service=service,
            monday=check_field(line, 'monday'),
            tuesday=check_field(line, 'tuesday'),
            wednesday=check_field(line, 'wednesday'),
            thursday=check_field(line, 'thursday'),
            friday=check_field(line, 'friday'),
            saturday=check_field(line, 'saturday'),
            sunday=check_field(line, 'sunday'),
            start_date=start_date,
            end_date=end_date)


class CalendarDatesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'calendar_dates.txt', optional=True)

    @staticmethod
    def parse(line):
        pdate = check_field(line, 'date')
        calendar_date = date(int(pdate[0:4]), int(pdate[4:6]), int(pdate[6:8]))

        try:
            service_id = check_field(line, 'service_id')
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist, e:
            raise ParserException.for_args(e.args)

        try:
            type_id = check_field(line, 'exception_type')
            exception_type = ExceptionType.objects.get(value=type_id)
        except ExceptionType.DoesNotExist, e:
            raise ParserException.for_args(e.args)

        return CalendarDate.objects.get_or_create(
            service=service,
            date=calendar_date,
            exception_type=exception_type)


class RoutesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'routes.txt')

    @staticmethod
    def parse(line):
        try:
            route_type_id = check_field(line, 'route_type')
            route_type = RouteType.objects.get(value=route_type_id)
        except RouteType.DoesNotExist, e:
            raise ParserException.for_args(e.args)

        (route, created) = Route.objects.get_or_create(
            route_id=check_field(line, 'route_id'),
            short_name=check_field(line, 'route_short_name'),
            long_name=check_field(line, 'route_long_name'),
            route_type=route_type)

        # link related agency
        if check_field(line, 'agency_id', optional=True):
            try:
                agency_id = check_field(line, 'agency_id', optional=True)
                route.agency = Agency.objects.get(agency_id=agency_id)
            except Agency.DoesNotExist, e:
                # raise ParserException(e.message)
                pass
                # raise ParserException('No agency with id %s '
                #                       % check_field(line, 'agency_id'))
                # self.stderr.write(
                #     'No agency with id %s ' % check_field(line,
                #                                           'agency_id'))

        # Optional parameters
        route.desc = check_field(line, 'route_desc', optional=True)
        route.url = check_field(line, 'route_url', optional=True)
        route.color = check_field(line, 'route_color', optional=True)
        route.text_color = check_field(line, 'route_text_color', optional=True)

        return route, created


class ShapesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'shapes.txt', optional=True)

    @staticmethod
    def parse(line):
        geopoint = BaseParser.create_geopoint(
            check_field(line, 'shape_pt_lat'),
            check_field(line, 'shape_pt_lon'))

        shape_id = check_field(line, 'shape_id')
        pt_sequence = check_field(line, 'shape_pt_sequence')

        shape, created = Shape.objects.get_or_create(
            shape_id=shape_id,
            geopoint=geopoint,
            pt_sequence=pt_sequence
        )

        # Optional parameters
        shape.dist_traveled = check_field(
            line, 'shape_dist_traveled', optional=True)

        return shape, created


class StopTimesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'stop_times.txt')

    @staticmethod
    def parse(line):
        # workaround here to prevent script from failing when there is no
        # arrival time or departure time fields.
        if check_field(line, 'arrival_time', optional=True) is None:
            (hour, minute, sec) = 0, 0, 0
        else:
            field = check_field(line, 'arrival_time')
            try:
                (hour, minute, sec) = map(int, field.split(':'))
            except ValueError, e:
                raise ParserException.for_args(e.args)
        arrival_time = time(hour % 24, minute % 60, sec % 60)

        if check_field(line, 'departure_time', optional=True) is None:
            (hour, minute, sec) = 0, 0, 0
        else:
            field = check_field(line, 'departure_time')
            try:
                (hour, minute, sec) = map(int, field.split(':'))
            except ValueError, e:
                raise ParserException.for_args(e.args)
        departure_time = time(hour % 24, minute % 60, sec % 60)

        try:
            trip = Trip.objects.get(trip_id=check_field(line, 'trip_id'))
            stop = Stop.objects.get(stop_id=check_field(line, 'stop_id'))
        except Trip.DoesNotExist, e:
            raise ParserException.for_args(e.args)
        except Stop.DoesNotExist, e:
            raise ParserException.for_args(e.args)

        stop_sequence = check_field(line, 'stop_sequence')

        (stop, created) = StopTime.objects.get_or_create(
            trip=trip,
            stop=stop,
            arrival_time=arrival_time,
            departure_time=departure_time,
            stop_sequence=stop_sequence
        )

        # create pickup_type
        if check_field(line, 'pickup_type', optional=True):
            try:
                pickup_type = check_field(line, 'pickup_type')
                stop.pickup_type = PickupType.objects.get(value=pickup_type)
            except PickupType.DoesNotExist, e:
                # raise ParserException.for_args(e.args)
                pass

        # check drop off type :
        if check_field(line, 'drop_off_type', optional=True):
            try:
                drop_off_type = check_field(line, 'drop_off_type')
                stop.drop_off_type = DropOffType.objects.get(value=drop_off_type)
            except DropOffType.DoesNotExist, e:
                # raise ParserException(e.message)
                pass

        return stop, created


class StopsParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'stops.txt')

    @staticmethod
    def parse(line):
        stop_id = check_field(line, 'stop_id')
        geopoint = BaseParser.create_geopoint(
            check_field(line, 'stop_lat'),
            check_field(line, 'stop_lon'))

        (stop, created) = Stop.objects.get_or_create(
            stop_id=stop_id,
            name=check_field(line, 'stop_name'),
            geopoint=geopoint)

        # create zone
        if check_field(line, 'zone_id', optional=True):
            zone_id = check_field(line, 'zone_id')
            (zone, created) = Zone.objects.get_or_create(zone_id=zone_id)

            stop.zone = zone

        # check parent station
        if check_field(line, 'parent_station', optional=True):
            try:
                parent_id = check_field(line, 'parent_station', optional=True)
                stop.parent_station = Stop.objects.get(stop_id=parent_id)
            except Stop.DoesNotExist, e:
                # raise ParserException.for_args(e.args)
                pass

        # Optional parameters
        stop.desc = check_field(line, 'stop_desc', optional=True)
        stop.url = check_field(line, 'stop_url', optional=True)
        stop.code = check_field(line, 'stop_code', optional=True)
        stop.location_type = check_field(line, 'location_type', optional=True)

        return stop, created


class TripsParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'trips.txt')

    @staticmethod
    def parse(line):
        route_id = check_field(line, 'route_id')
        route = Route.objects.get(route_id=route_id)

        service_id = check_field(line, 'service_id')
        service = Service.objects.get_or_create(service_id=service_id)[0]

        trip_id = check_field(line, 'trip_id')

        (trip, created) = Trip.objects.get_or_create(
            route=route,
            service=service,
            trip_id=trip_id)

        # link related direction_id
        if check_field(line, 'direction_id', optional=True):
            direction_id = check_field(line, 'direction_id')
            print 'Directions: ', Direction.objects.get(value=direction_id)
            trip.direction = Direction.objects.get(value=direction_id)

        if check_field(line, 'block_id', optional=True):
            block_id = check_field(line, 'block_id')
            trip.block = Block.objects.get_or_create(block_id=block_id)[0]

        # Optional parameters
        trip.headsign = check_field(line, 'trip_headsign', optional=True)
        trip.shape_id = check_field(line, 'shape_id', optional=True)

        return trip, created