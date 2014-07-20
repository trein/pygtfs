from django.test import TestCase
from service.parsers import *

ROOT_DIR = 'service/tests/data/sample-feed'


class BaseParserTest(TestCase):
    def setUp(self):
        self.subject = CalendarDatesParser()


class AgencyTest(TestCase):
    def setUp(self):
        self.subject = AgencyParser()

    def test_agencies_can_be_parsed(self):
        line = {
            'agency_name': 'Demo Transit Authority',
            'agency_url': 'http://google.com',
            'agency_timezone': 'America/Los_Angeles',
            'agency_id': 'DTA',
            'agency_lang': 'en',
            'agency_phone': '555-555-5555',
            'agency_fare_url': 'http://google.com',
        }
        (actual, created) = self.subject.parse(line)

        expected = Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            agency_id='DTA',
            lang='en',
            phone='555-555-5555',
            fare_url='http://google.com',
        )
        self.assertEqual(actual, expected)

    def test_agencies_consider_optional_agency_id(self):
        line = {
            'agency_name': 'Demo Transit Authority',
            'agency_url': 'http://google.com',
            'agency_timezone': 'America/Los_Angeles',
            'agency_lang': 'en',
            'agency_phone': '555-555-5555',
            'agency_fare_url': 'http://google.com',
        }
        (actual, created) = self.subject.parse(line)

        expected = Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            lang='en',
            phone='555-555-5555',
            fare_url='http://google.com',
        )
        self.assertEqual(actual, expected)

    def test_agencies_consider_optional_lang(self):
        line = {
            'agency_name': 'Demo Transit Authority',
            'agency_url': 'http://google.com',
            'agency_timezone': 'America/Los_Angeles',
            'agency_id': 'DTA',
            'agency_phone': '555-555-5555',
            'agency_fare_url': 'http://google.com',
        }
        (actual, created) = self.subject.parse(line)

        expected = Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            agency_id='DTA',
            phone='555-555-5555',
            fare_url='http://google.com',
        )
        self.assertEqual(actual, expected)

    def test_agencies_consider_optional_phone(self):
        line = {
            'agency_name': 'Demo Transit Authority',
            'agency_url': 'http://google.com',
            'agency_timezone': 'America/Los_Angeles',
            'agency_id': 'DTA',
            'agency_lang': 'en',
            'agency_fare_url': 'http://google.com',
        }
        (actual, created) = self.subject.parse(line)

        expected = Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            agency_id='DTA',
            lang='en',
            fare_url='http://google.com',
        )
        self.assertEqual(actual, expected)

    def test_agencies_consider_optional_fare_url(self):
        line = {
            'agency_name': 'Demo Transit Authority',
            'agency_url': 'http://google.com',
            'agency_timezone': 'America/Los_Angeles',
            'agency_id': 'DTA',
            'agency_lang': 'en',
            'agency_phone': '555-555-5555',
        }
        (actual, created) = self.subject.parse(line)

        expected = Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            agency_id='DTA',
            lang='en',
            phone='555-555-5555',
        )
        self.assertEqual(actual, expected)


class CalendarTest(TestCase):
    def setUp(self):
        self.fixture()
        self.subject = CalendarParser()

    def fixture(self):
        # database setup
        Service(service_id='FULLW').save()

    def test_calendar_can_be_parsed(self):
        line = {
            'end_date': '20101231',
            'start_date': '20070101',
            'monday': '1',
            'tuesday': '1',
            'wednesday': '1',
            'thursday': '1',
            'friday': '1',
            'saturday': '1',
            'sunday': '1',
            'service_id': 'FULLW',
        }
        (actual, created) = self.subject.parse(line)

        expected = Calendar(
            end_date=date(year=2010, month=12, day=31),
            start_date=date(year=2007, month=01, day=01),
            monday='1',
            tuesday='1',
            wednesday='1',
            thursday='1',
            friday='1',
            saturday='1',
            sunday='1',
            service=Service.objects.get(service_id='FULLW'),
        )
        self.assertEqual(actual, expected)

    def test_calendar_detect_incomplete_format(self):
        line = {
            'end_date': '20101231',
            'start_date': '20070101',
            'tuesday': '1',
            'wednesday': '1',
            'thursday': '1',
            'friday': '1',
            'saturday': '1',
            'sunday': '1',
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_calendar_invalid_service_id(self):
        line = {
            'end_date': '20101231',
            'start_date': '20070101',
            'monday': '1',
            'tuesday': '1',
            'wednesday': '1',
            'thursday': '1',
            'friday': '1',
            'saturday': '1',
            'sunday': '1',
            'service_id': 'INVALID',
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_calendar_invalid_date(self):
        line = {
            'end_date': '0101213',
            'start_date': '20070101',
            'monday': '1',
            'tuesday': '1',
            'wednesday': '1',
            'thursday': '1',
            'friday': '1',
            'saturday': '1',
            'sunday': '1',
            'service_id': 'FULLW',
        }
        self.assertRaises(ValueError, self.subject.parse, line)


class CalendarDatesParserTest(TestCase):
    def setUp(self):
        self.fixture()
        self.subject = CalendarDatesParser()

    def fixture(self):
        # database setup
        Service(service_id='FULLW').save()
        ExceptionType(value=2, name='none').save()

    def test_calendar_dates_can_be_parsed(self):
        line = {
            'date': '20070604', 'service_id': 'FULLW', 'exception_type': '2'
        }
        (actual, created) = self.subject.parse(line)

        expected = CalendarDate(
            service=Service.objects.get(service_id='FULLW'),
            date=date(year=2007, month=06, day=04),
            exception_type=ExceptionType.objects.get(value=2)
        )
        self.assertEqual(actual, expected)

    def test_calendar_dates_detect_incomplete_date(self):
        line = {
            'date': '2007060', 'service_id': 'FULLW', 'exception_type': '2'
        }
        self.assertRaises(ValueError, self.subject.parse, line)

    def test_calendar_dates_detect_incomplete_format(self):
        line = {
            'date': '20070604', 'service_id': 'FULLW'
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_calendar_dates_detect_invalid_service_id(self):
        line = {
            'date': '20070604', 'service_id': 'NOT', 'exception_type': '2'
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_calendar_dates_detect_invalid_exception_type(self):
        line = {
            'date': '20070604', 'service_id': 'FULLW', 'exception_type': '-1'
        }
        self.assertRaises(ParserException, self.subject.parse, line)


class RoutesParserTest(TestCase):
    def setUp(self):
        self.fixture()
        self.subject = RoutesParser()

    def fixture(self):
        RouteType(name='one', description='desc', value=3).save()
        Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            agency_id='DTA',
            lang='en',
            phone='555-555-5555',
        ).save()

    def test_routes_can_be_parsed(self):
        line = {
            'agency_id': 'DTA',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_type': '3',
            'route_desc': '',
            'route_url': '',
            'route_color': '',
            'route_text_color': '',
        }
        (actual, created) = self.subject.parse(line)

        expected = Route(
            agency=Agency.objects.get(agency_id='DTA'),
            route_id='AB',
            short_name='10',
            long_name='Airport - Bullfrog',
            route_type=RouteType.objects.get(value=3),
            desc=None,
            url=None,
            color='FFFFFF',
            text_color='000000',
        )
        self.assertEqual(actual, expected)

    def test_routes_detect_incomplete_format(self):
        line = {
            'agency_id': 'DTA',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_desc': '',
            'route_url': '',
            'route_color': '',
            'route_text_color': '',
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_routes_detect_invalid_agency(self):
        line = {
            'agency_id': 'INVALID',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_type': '3',
            'route_desc': '',
            'route_url': '',
            'route_color': '',
            'route_text_color': '',
        }
        # Exception currently removed
        # self.assertRaises(ParserException, self.subject.parse, line)

    def test_routes_detect_invalid_route_type(self):
        line = {
            'agency_id': 'DTA',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_type': '123',
            'route_desc': '',
            'route_url': '',
            'route_color': '',
            'route_text_color': '',
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_routes_consider_optional_desc(self):
        line = {
            'agency_id': 'DTA',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_type': '3',
            'route_url': '',
            'route_color': '',
            'route_text_color': '',
        }
        (actual, created) = self.subject.parse(line)

        expected = Route(
            agency=Agency.objects.get(agency_id='DTA'),
            route_id='AB',
            short_name='10',
            long_name='Airport - Bullfrog',
            route_type=RouteType.objects.get(value=3),
            desc=None,
            url=None,
            color='FFFFFF',
            text_color='000000',
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_url(self):
        line = {
            'agency_id': 'DTA',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_type': '3',
            'route_desc': '',
            'route_url': '',
            'route_color': '',
            'route_text_color': '',
        }
        (actual, created) = self.subject.parse(line)

        expected = Route(
            agency=Agency.objects.get(agency_id='DTA'),
            route_id='AB',
            short_name='10',
            long_name='Airport - Bullfrog',
            route_type=RouteType.objects.get(value=3),
            desc=None,
            url=None,
            color='FFFFFF',
            text_color='000000',
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_color(self):
        line = {
            'agency_id': 'DTA',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_type': '3',
            'route_desc': '',
            'route_url': '',
            'route_text_color': '',
        }
        (actual, created) = self.subject.parse(line)

        expected = Route(
            agency=Agency.objects.get(agency_id='DTA'),
            route_id='AB',
            short_name='10',
            long_name='Airport - Bullfrog',
            route_type=RouteType.objects.get(value=3),
            desc=None,
            url=None,
            color='FFFFFF',
            text_color='000000',
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_text_color(self):
        line = {
            'agency_id': 'DTA',
            'route_id': 'AB',
            'route_short_name': '10',
            'route_long_name': 'Airport - Bullfrog',
            'route_type': '3',
            'route_desc': '',
            'route_url': '',
            'route_color': '',
        }
        (actual, created) = self.subject.parse(line)

        expected = Route(
            agency=Agency.objects.get(agency_id='DTA'),
            route_id='AB',
            short_name='10',
            long_name='Airport - Bullfrog',
            route_type=RouteType.objects.get(value=3),
            desc=None,
            url=None,
            color='FFFFFF',
            text_color='000000',
        )
        self.assertEqual(actual, expected)


class ShapeParserTest(TestCase):
    def setUp(self):
        self.subject = ShapesParser()

    def test_routes_can_be_parsed(self):
        line = {
            'shape_id': '180-2',
            'shape_pt_lat': '-30.027275',
            'shape_pt_lon': '-51.22919',
            'shape_pt_sequence': '1',
            'shape_dist_traveled': '100'
        }
        (actual, created) = self.subject.parse(line)

        expected = Shape(
            shape_id='180-2',
            geopoint=Point(-30.027275, -51.22919),
            pt_sequence='1',
            dist_traveled='100',
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_dist(self):
        line = {
            'shape_id': '180-2',
            'shape_pt_lat': '-30.027275',
            'shape_pt_lon': '-51.22919',
            'shape_pt_sequence': '1',
        }
        (actual, created) = self.subject.parse(line)

        expected = Shape(
            shape_id='180-2',
            geopoint=Point(-30.027275, -51.22919),
            pt_sequence='1',
            dist_traveled=None,
        )
        self.assertEqual(actual, expected)

    def test_routes_detect_invalid_format(self):
        line = {
            'shape_pt_lat': '-30.027275',
            'shape_pt_lon': '-51.22919',
            'shape_pt_sequence': '1',
        }
        self.assertRaises(ParserException, self.subject.parse, line)


class StopTimesParserTest(TestCase):
    def setUp(self):
        self.fixture()
        self.subject = StopTimesParser()

    def fixture(self):
        RouteType(name='one', description='desc', value=3).save()
        Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            agency_id='DTA',
            lang='en',
            phone='555-555-5555',
        ).save()
        Service(service_id='FULLW').save()
        Route(
            agency=Agency.objects.get(agency_id='DTA'),
            route_id='AB',
            short_name='10',
            long_name='Airport - Bullfrog',
            route_type=RouteType.objects.get(value=3),
        ).save()
        Trip(
            trip_id='STBA',
            route=Route.objects.get(route_id='AB'),
            service=Service.objects.get(service_id='FULLW'),
            headsign='a'
        ).save()
        Stop(
            stop_id='STAGECOACH',
            name='stop',
            geopoint=Point(-32.124, 50.123),
        ).save()

    def test_routes_can_be_parsed(self):
        line = {
            'pickup_type': '',
            'drop_off_time': '',
            'trip_id': 'STBA',
            'stop_id': 'STAGECOACH',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '6:00:00',
            'departure_time': '6:00:00'
        }
        (actual, created) = self.subject.parse(line)

        expected = StopTime(
            trip=Trip.objects.get(trip_id='STBA'),
            stop=Stop.objects.get(stop_id='STAGECOACH'),
            arrival_time=time(6 % 24, 0 % 60, 0 % 60),
            departure_time=time(6 % 24, 0 % 60, 0 % 60),
            stop_sequence='1'
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_arrival_time(self):
        line = {
            'pickup_type': '',
            'drop_off_time': '',
            'trip_id': 'STBA',
            'stop_id': 'STAGECOACH',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '',
            'departure_time': '6:00:00'
        }
        (actual, created) = self.subject.parse(line)

        expected = StopTime(
            trip=Trip.objects.get(trip_id='STBA'),
            stop=Stop.objects.get(stop_id='STAGECOACH'),
            arrival_time=time(0 % 24, 0 % 60, 0 % 60),
            departure_time=time(6 % 24, 0 % 60, 0 % 60),
            stop_sequence='1'
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_departure_time(self):
        line = {
            'pickup_type': '',
            'drop_off_time': '',
            'trip_id': 'STBA',
            'stop_id': 'STAGECOACH',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '6:00:00',
            'departure_time': ''
        }
        (actual, created) = self.subject.parse(line)

        expected = StopTime(
            trip=Trip.objects.get(trip_id='STBA'),
            stop=Stop.objects.get(stop_id='STAGECOACH'),
            arrival_time=time(6 % 24, 0 % 60, 0 % 60),
            departure_time=time(0 % 24, 0 % 60, 0 % 60),
            stop_sequence='1'
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_pickup_type(self):
        line = {
            'drop_off_time': '',
            'trip_id': 'STBA',
            'stop_id': 'STAGECOACH',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '6:00:00',
            'departure_time': '6:00:00'
        }
        (actual, created) = self.subject.parse(line)

        expected = StopTime(
            trip=Trip.objects.get(trip_id='STBA'),
            stop=Stop.objects.get(stop_id='STAGECOACH'),
            arrival_time=time(6 % 24, 0 % 60, 0 % 60),
            departure_time=time(6 % 24, 0 % 60, 0 % 60),
            stop_sequence='1'
        )
        self.assertEqual(actual, expected)

    def test_routes_consider_optional_drop_off_type(self):
        line = {
            'pickup_type': '',
            'trip_id': 'STBA',
            'stop_id': 'STAGECOACH',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '6:00:00',
            'departure_time': '6:00:00'
        }
        (actual, created) = self.subject.parse(line)

        expected = StopTime(
            trip=Trip.objects.get(trip_id='STBA'),
            stop=Stop.objects.get(stop_id='STAGECOACH'),
            arrival_time=time(6 % 24, 0 % 60, 0 % 60),
            departure_time=time(6 % 24, 0 % 60, 0 % 60),
            stop_sequence='1'
        )
        self.assertEqual(actual, expected)

    def test_routes_detect_invalid_time(self):
        line = {
            'pickup_type': '',
            'drop_off_time': '',
            'trip_id': 'STBA',
            'stop_id': 'STAGECOACH',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '6:0000',
            'departure_time': '6:00:00'
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_routes_detect_invalid_trip(self):
        line = {
            'pickup_type': '',
            'drop_off_time': '',
            'trip_id': 'INVALID',
            'stop_id': 'STAGECOACH',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '6:00:00',
            'departure_time': '6:00:00'
        }
        self.assertRaises(ParserException, self.subject.parse, line)

    def test_routes_detect_invalid_stio(self):
        line = {
            'pickup_type': '',
            'drop_off_time': '',
            'trip_id': 'STBA',
            'stop_id': 'INVALID',
            'stop_headsign': '',
            'stop_sequence': '1',
            'shape_dist_traveled': '',
            'arrival_time': '6:00:00',
            'departure_time': '6:00:00'
        }
        self.assertRaises(ParserException, self.subject.parse, line)


class StopsParserTest(TestCase):
    def setUp(self):
        self.fixture()
        self.subject = StopsParser()

    def fixture(self):
        WheelchairAccessible(value=1, name='PARTICULAR').save()
        Zone(zone_id='ZONE').save()

    def test_stops_can_be_parsed(self):
        line = {
            'stop_id': 'FUR_CREEK_RES',
            'stop_lat': '36.425288',
            'stop_lon': '-117.133162',
            'stop_name': 'Furnace Creek Resort (Demo)',
            'stop_url': '',
            'stop_desc': '',
            'stop_code': 'NO_CODE',
            'zone_id': 'ZONE',
            'location_type': '1',
            'parent_station': '',
            'wheelchair_boarding': '1',
        }
        (actual, created) = self.subject.parse(line)

        expected = Stop(
            stop_id='FUR_CREEK_RES',
            code='NO_CODE',
            name='Furnace Creek Resort (Demo)',
            url=None,
            desc=None,
            zone=Zone.objects.get(zone_id='ZONE'),
            location_type='1',
            parent_station=None,
            wheelchair=WheelchairAccessible.objects.get(value=1),
            geopoint=Point(36.425288, -117.133162),
        )
        self.assertEqual(actual, expected)


class TripsParserTest(TestCase):
    def setUp(self):
        self.fixture()
        self.subject = TripsParser()

    def fixture(self):
        WheelchairAccessible(value=1, name='PARTICULAR').save()
        RouteType(name='one', description='desc', value=3).save()
        Agency(
            url='http://google.com',
            name='Demo Transit Authority',
            timezone='America/Los_Angeles',
            agency_id='DTA',
            lang='en',
            phone='555-555-5555',
        ).save()
        Service(service_id='FULLW').save()
        Route(
            route_id='AB',
            agency=Agency.objects.get(agency_id='DTA'),
            short_name='10',
            long_name='Airport - Bullfrog',
            route_type=RouteType.objects.get(value=3),
        ).save()
        Direction(value=0, name='to Downtown').save()
        Shape(
            shape_id='180-2',
            geopoint=Point(-30.027275, -51.22919),
            pt_sequence='1',
            dist_traveled='100',
        ).save()

    def test_trips_can_be_parsed(self):
        line = {
            'trip_id': 'AB1',
            'block_id': '1',
            'route_id': 'AB',
            'service_id': 'FULLW',
            'direction_id': '0',
            'shape_id': '180-2',
            'trip_headsign': 'to Bullfrog',
            'wheelchair_accessible': '1',
            'short_name': 'AB_TEST',
        }
        (actual, created) = self.subject.parse(line)

        expected = Trip(
            trip_id='AB1',
            route=Route.objects.get(route_id='AB'),
            service=Service.objects.get(service_id='FULLW'),
            direction=Direction.objects.get(value=0),
            block=Block.objects.get(block_id='1'),
            headsign='to Bullfrog',
            wheelchair=WheelchairAccessible.objects.get(value=1),
            short_name='AB_TEST',
        )
        self.assertEqual(actual, expected)
