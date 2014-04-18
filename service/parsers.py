from django.contrib.gis.geos import fromstr
from service.models import *
from datetime import time
from datetime import date


class ParserException(Exception):
    @staticmethod
    def for_message(message):
        return ParserException(message)


def check_field(reader, field, optional=False):
    if field in reader and reader[field]:
        return reader[field]
    elif not optional:
        raise ParserException.for_message(
            "Field %s was empty or non-present in file" % field)
    return None


class BaseParser(object):
    def __init__(self, filename, optional=False, fields=[]):
        self.filename = filename
        self.optional = optional
        self.fields = fields

    @staticmethod
    def parse(line):
        raise ParserException("Parser methods not implemented.")

    @staticmethod
    def create_geopoint(lat, lng):
        return fromstr("POINT(%s %s)" % (float(lat), float(lng)))


class CalendarDatesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, "calendar_dates.txt", optional=True)

    @staticmethod
    def parse(line):
        pdate = check_field(line, 'date')
        calendar_date = date(int(pdate[0:4]), int(pdate[4:6]), int(pdate[6:8]))

        service_id = check_field(line, 'service_id')
        service = Service.objects.get(service_id=service_id)

        type_id = check_field(line, 'exception_type')
        exception_type = ExceptionType.objects.get(value=type_id)

        return CalendarDate.objects.get_or_create(
            service=service,
            date=calendar_date,
            exception_type=exception_type)


class CalendarParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, "calendar.txt", optional=False)

    @staticmethod
    def parse(line):
        temp = check_field(line, 'start_date')
        start_date = date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))

        temp = check_field(line, 'end_date')
        end_date = date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))

        service_id = check_field(line, 'service_id')
        service = Service.objects.get(service_id=service_id)

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


class StopTimesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, "stop_times.txt", optional=False)

    @staticmethod
    def parse(line):
        # workaround here to prevent script from failing when there is no
        # arrival time or departure time fields.
        if check_field(line, 'arrival_time', optional=True) is None:
            (hour, minute, sec) = 0, 0, 0
        else:
            field = check_field(line, 'arrival_time')
            (hour, minute, sec) = map(int, field.split(":"))
        arrival_time = time(hour % 24, minute % 60, sec % 60)

        if check_field(line, 'departure_time', optional=True) is None:
            (hour, minute, sec) = 0, 0, 0
        else:
            field = check_field(line, 'departure_time')
            (hour, minute, sec) = map(int, field.split(":"))
        departure_time = time(hour % 24, minute % 60, sec % 60)

        trip = Trip.objects.get(trip_id=check_field(line, 'trip_id'))
        stop = Stop.objects.get(stop_id=check_field(line, 'stop_id'))
        stop_sequence = check_field(line, 'stop_sequence')

        (stop, created) = StopTime.objects.get_or_create(
            trip=trip,
            stop=stop,
            arrival_time=arrival_time,
            departure_time=departure_time,
            stop_sequence=stop_sequence)

        # create pickup_type
        if check_field(line, 'pickup_type', optional=True):
            pickup_type = check_field(line, 'pickup_type')
            stop.pickup_type = PickupType.objects.get(value=pickup_type)

        # check drop off type :
        if check_field(line, 'drop_off_type', optional=True):
            drop_off_type = check_field(line, 'drop_off_type')
            stop.drop_off_type = DropOffType.objects.get(value=drop_off_type)

        return stop, created


class StopsParser(BaseParser):
    fields = [('desc', 'stop_desc'),
              ('code', 'stop_code'),
              ('url', 'stop_url'),
              ('location_type', 'location_type')]

    def __init__(self):
        BaseParser.__init__(self, "stops.txt", optional=False, fields=fields)

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
                stop_id = check_field(line, 'parent_station', optional=True)
                stop.parent_station = Stop.objects.get(stop_id=stop_id)
            except Exception, e:
                pass
        return stop, created


class RoutesParser(BaseParser):
    fields = [('desc', 'route_desc'),
              ('url', 'route_url'),
              ('color', 'route_color'),
              ('text_color', 'route_text_color')]

    def __init__(self):
        BaseParser.__init__(self, "routes.txt", optional=False, fields=fields)

    @staticmethod
    def parse(line):
        route_id = check_field(line, 'route_id')
        short_name = check_field(line, 'route_short_name')
        long_name = check_field(line, 'route_long_name')
        route_type_id = check_field(line, 'route_type')
        route_type = RouteType.objects.get(value=route_type_id)

        (route, created) = Route.objects.get_or_create(
            route_id=route_id,
            short_name=short_name,
            long_name=long_name,
            route_type=route_type)

        # link related agency
        if check_field(line, 'agency_id', optional=True):
            try:
                agency_id = check_field(line, 'agency_id')
                route.agency = Agency.objects.get(agency_id=agency_id)
            except Exception, e:
                # raise ParserException("No agency with id %s "
                #                       % check_field(line, 'agency_id'))
                self.stderr.write(
                    "No agency with id %s " % check_field(line,
                                                          'agency_id'))
        return route, created


class TripsParser(BaseParser):
    fields = [('headsign', 'trip_headsign'),
              ('shape_id', 'shape_id')]

    def __init__(self):
        BaseParser.__init__(self, "trips.txt", optional=False, fields=fields)

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
            trip.direction = Direction.objects.get(value=direction_id)

        if check_field(line, 'block_id', optional=True):
            block_id = check_field(line, 'block_id')
            trip.block = Block.objects.get_or_create(block_id=block_id)[0]

        return trip, created


class ShapesParser(BaseParser):
    fields = [('dist_traveled', 'shape_dist_traveled')]

    def __init__(self):
        BaseParser.__init__(self, "shapes.txt", optional=True, fields=fields)

    @staticmethod
    def parse(line):
        geopoint = BaseParser.create_geopoint(
            check_field(line, 'shape_pt_lat'),
            check_field(line, 'shape_pt_lon'))

        shape_id = check_field(line, 'shape_id')
        pt_sequence = check_field(line, 'shape_pt_sequence')

        return Shape.objects.get_or_create(
            shape_id=shape_id,
            geopoint=geopoint,
            pt_sequence=pt_sequence)


class AgencyParser(BaseParser):
    fields = [('agency_id', 'agency_id'),
              ('lang', 'agency_lang'),
              ('phone', 'agency_phone'),
              ('fare_url', 'agency_fare_url')]

    def __init__(self):
        BaseParser.__init__(self, "agency.txt", optional=False, fields=fields)

    @staticmethod
    def parse(line):
        name = check_field(line, 'agency_name')
        url = check_field(line, 'agency_url')
        timezone = check_field(line, 'agency_timezone')

        return Agency.objects.get_or_create(
            name=name, url=url, timezone=timezone)