from datetime import time
from datetime import date
from service.models import *


class ParserException(Exception):
    @staticmethod
    def for_message(message):
        return ParserException(message)

    @staticmethod
    def for_args(*args):
        return ParserException(*args)


class BaseParser(object):
    def __init__(self, filename, optional=False):
        self.filename = filename
        self.optional = optional

    def parse(self, line):
        raise ParserException('Parser methods not implemented.')

    def _create(self, model_class, mandatory, optional=None):
        (entity, created) = model_class.objects.get_or_create(**mandatory)
        if optional:
            self._update(entity, optional)
        entity.save()
        return entity, created

    @staticmethod
    def _update(model, params):
        for key, value in params.iteritems():
            if value:
                model.update_param(key, value)

    @staticmethod
    def field(line, field, optional=False):
        if field in line and line[field]:
            return line[field]
        elif not optional:
            raise ParserException.for_message(
                'Field %s was empty or non-present in file' % field)
        return None


class AgencyParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'agency.txt')

    def parse(self, line):
        mandatory = {
            'name': self.field(line, 'agency_name'),
            'url': self.field(line, 'agency_url'),
            'timezone': self.field(line, 'agency_timezone'),
        }
        optional = {
            'agency_id': self.field(line, 'agency_id', optional=True),
            'lang': self.field(line, 'agency_lang', optional=True),
            'phone': self.field(line, 'agency_phone', optional=True),
            'fare_url': self.field(line, 'agency_fare_url', optional=True),
        }
        return self._create(Agency, mandatory, optional)


class CalendarParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'calendar.txt')

    def _parse_start(self, line):
        temp = self.field(line, 'start_date')
        start_date = date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))
        return start_date

    def _parse_end(self, line):
        temp = self.field(line, 'end_date')
        end_date = date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))
        return end_date

    def _parse_service(self, line):
        try:
            service_id = self.field(line, 'service_id')
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist as e:
            raise ParserException.for_args(e.args)
        return service

    def parse(self, line):
        mandatory = {
            'monday': self.field(line, 'monday'),
            'tuesday': self.field(line, 'tuesday'),
            'wednesday': self.field(line, 'wednesday'),
            'thursday': self.field(line, 'thursday'),
            'friday': self.field(line, 'friday'),
            'saturday': self.field(line, 'saturday'),
            'sunday': self.field(line, 'sunday'),
            'service': self._parse_service(line),
            'start_date': self._parse_start(line),
            'end_date': self._parse_end(line),
        }
        return self._create(Calendar, mandatory)


class CalendarDatesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'calendar_dates.txt', optional=True)

    def _parse_exception(self, line):
        try:
            type_id = self.field(line, 'exception_type')
            exception_type = ExceptionType.objects.get(value=type_id)
        except ExceptionType.DoesNotExist as e:
            raise ParserException.for_args(e.args)
        return exception_type

    def _parse_service(self, line):
        try:
            service_id = self.field(line, 'service_id')
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist as e:
            raise ParserException.for_args(e.args)
        return service

    def _parse_date(self, line):
        pdate = self.field(line, 'date')
        calendar_date = date(int(pdate[0:4]), int(pdate[4:6]), int(pdate[6:8]))
        return calendar_date

    def parse(self, line):
        mandatory = {
            'service': self._parse_service(line),
            'date': self._parse_date(line),
            'exception_type': self._parse_exception(line),
        }
        return self._create(CalendarDate, mandatory)


class RoutesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'routes.txt')

    def _parse_route_type(self, line):
        route_type = None
        try:
            route_type_id = self.field(line, 'route_type')
            route_type = RouteType.objects.get(value=route_type_id)
        except RouteType.DoesNotExist as e:
            raise ParserException.for_args(e.args)
        return route_type

    def _parse_agency(self, line):
        agency = None
        if self.field(line, 'agency_id', optional=True):
            try:
                agency_id = self.field(line, 'agency_id', optional=True)
                agency = Agency.objects.get(agency_id=agency_id)
            except Agency.DoesNotExist as e:
                raise ParserException.for_args(e.args)
                # raise ParserException('No agency with id %s '
                #                       % check_self.field(line, 'agency_id'))
                # self.stderr.write(
                #     'No agency with id %s ' % check_self.field(line,
                #                                           'agency_id'))
        return agency

    def parse(self, line):
        mandatory = {
            'route_id': self.field(line, 'route_id'),
            'short_name': self.field(line, 'route_short_name'),
            'long_name': self.field(line, 'route_long_name'),
            'route_type': self._parse_route_type(line),
        }
        optional = {
            'agency': self._parse_agency(line),
            'desc': self.field(line, 'route_desc', optional=True),
            'url': self.field(line, 'route_url', optional=True),
            'color': self.field(line, 'route_color', optional=True),
            'text_color': self.field(line, 'route_text_color', optional=True),
        }
        return self._create(Route, mandatory, optional)


class ShapesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'shapes.txt', optional=True)

    def parse(self, line):
        geopoint = [
            float(self.field(line, 'shape_pt_lat')),
            float(self.field(line, 'shape_pt_lon'))]
        mandatory = {
            'geopoint': geopoint,
            'shape_id': self.field(line, 'shape_id'),
            'pt_sequence': self.field(line, 'shape_pt_sequence'),
        }
        optional = {
            'dist_traveled': self.field(line, 'shape_dist_traveled',
                                        optional=True),
        }
        return self._create(Shape, mandatory, optional)


class StopTimesParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'stop_times.txt')

    def _parse_drop_off(self, line):
        drop_off_type = None
        if self.field(line, 'drop_off_type', optional=True):
            try:
                drop_off_type = self.field(line, 'drop_off_type')
                drop_off_type = DropOffType.objects.get(value=drop_off_type)
            except DropOffType.DoesNotExist:
                # except DropOffType.DoesNotExist, e:
                # raise ParserException(e.message)
                pass
        return drop_off_type

    def _parse_arrival(self, line):
        if self.field(line, 'arrival_time', optional=True) is None:
            (hour, minute, sec) = 0, 0, 0
        else:
            field = self.field(line, 'arrival_time')
            try:
                (hour, minute, sec) = map(int, field.split(':'))
            except ValueError as e:
                raise ParserException.for_args(e.args)
        arrival_time = time(hour % 24, minute % 60, sec % 60)
        return arrival_time

    def _parse_departure(self, line):
        if self.field(line, 'departure_time', optional=True) is None:
            (hour, minute, sec) = 0, 0, 0
        else:
            field = self.field(line, 'departure_time')
            try:
                (hour, minute, sec) = map(int, field.split(':'))
            except ValueError as e:
                raise ParserException.for_args(e.args)
        departure_time = time(hour % 24, minute % 60, sec % 60)
        return departure_time

    def _parse_pickup(self, line):
        pickup_type = None
        if self.field(line, 'pickup_type', optional=True):
            try:
                pickup_type = self.field(line, 'pickup_type')
                pickup_type = PickupType.objects.get(value=pickup_type)
            except PickupType.DoesNotExist:
                pass
                # except PickupType.DoesNotExist, e:
                #     raise ParserException.for_args(e.args)
        return pickup_type

    def _parse_trip(self, line):
        try:
            trip = Trip.objects.get(trip_id=self.field(line, 'trip_id'))
        except Trip.DoesNotExist as e:
            raise ParserException.for_args(e.args)
        return trip

    def _parse_stop(self, line):
        try:
            stop = Stop.objects.get(stop_id=self.field(line, 'stop_id'))
        except Stop.DoesNotExist as e:
            raise ParserException.for_args(e.args)
        return stop

    def parse(self, line):
        # workaround here to prevent script from failing when there is no
        # arrival time or departure time fields.
        mandatory = {
            'trip': self._parse_trip(line),
            'stop': self._parse_stop(line),
            'arrival_time': self._parse_arrival(line),
            'departure_time': self._parse_departure(line),
            'stop_sequence': self.field(line, 'stop_sequence'),
        }
        optional = {
            'pickup_type': self._parse_pickup(line),
            'drop_off_type': self._parse_drop_off(line),
        }
        return self._create(StopTime, mandatory, optional)


class StopsParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'stops.txt')

    def _parse_parent(self, line):
        parent_station = None
        if self.field(line, 'parent_station', optional=True):
            try:
                parent_id = self.field(line, 'parent_station', optional=True)
                parent_station = Stop.objects.get(stop_id=parent_id)
            except Stop.DoesNotExist:
                # except Stop.DoesNotExist, e:
                # raise ParserException.for_args(e.args)
                pass
        return parent_station

    def _parse_zone(self, line):
        zone = None
        if self.field(line, 'zone_id', optional=True):
            zone_id = self.field(line, 'zone_id')
            (zone, created) = Zone.objects.get_or_create(zone_id=zone_id)
        return zone

    def _parse_wheelchair(self, line):
        wheelchair = None
        if self.field(line, 'wheelchair_boarding', optional=True):
            wheelchair = self.field(line, 'wheelchair_boarding')
            wheelchair = WheelchairAccessible.objects.get(value=wheelchair)
        return wheelchair

    def parse(self, line):
        point = [
            float(self.field(line, 'stop_lat')),
            float(self.field(line, 'stop_lon'))]
        mandatory = {
            'stop_id': self.field(line, 'stop_id'),
            'name': self.field(line, 'stop_name'),
            'geopoint': point,
        }
        optional = {
            'zone': self._parse_zone(line),
            'parent_station': self._parse_parent(line),
            'wheelchair': self._parse_wheelchair(line),
            'desc': self.field(line, 'stop_desc', optional=True),
            'url': self.field(line, 'stop_url', optional=True),
            'code': self.field(line, 'stop_code', optional=True),
            'location_type': self.field(line, 'location_type', optional=True),
        }
        return self._create(Stop, mandatory, optional)


class TripsParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self, 'trips.txt')

    def _parse_directions(self, line):
        direction = None
        if self.field(line, 'direction_id', optional=True):
            direction_id = self.field(line, 'direction_id')
            direction = Direction.objects.get(value=direction_id)
        return direction

    def _parse_wheelchair(self, line):
        wheelchair = None
        if self.field(line, 'wheelchair_accessible', optional=True):
            wheelchair = self.field(line, 'wheelchair_accessible')
            wheelchair = WheelchairAccessible.objects.get(value=wheelchair)
        return wheelchair

    def _parse_block(self, line):
        block = None
        if self.field(line, 'block_id', optional=True):
            block_id = self.field(line, 'block_id')
            (block, c) = Block.objects.get_or_create(block_id=block_id)
        return block

    def _parse_service(self, line):
        service_id = self.field(line, 'service_id')
        service = Service.objects.get_or_create(service_id=service_id)[0]
        return service

    def _parse_route(self, line):
        route_id = self.field(line, 'route_id')
        route = Route.objects.get(route_id=route_id)
        return route

    def parse(self, line):
        mandatory = {
            'route': self._parse_route(line),
            'service': self._parse_service(line),
            'trip_id': self.field(line, 'trip_id'),
        }
        optional = {
            'headsign': self.field(line, 'trip_headsign', optional=True),
            'short_name': self.field(line, 'short_name', optional=True),
            'direction': self._parse_directions(line),
            'block': self._parse_block(line),
            'wheelchair': self._parse_wheelchair(line),
        }
        (entity, created) = self._create(Trip, mandatory, optional)

        if self.field(line, 'shape_id', optional=True):
            shape_id = self.field(line, 'shape_id')
            for shape in Shape.all_by_id(shape_id):
                if not entity.has_shape(shape):
                    entity.shapes.add(shape)
            entity.save()

        return entity, created
