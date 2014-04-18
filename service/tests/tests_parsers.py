from django.test import TestCase
from service.parsers import *

ROOT_DIR = 'service/tests/data/sample-feed'


class CalendarDatesParserTest(TestCase):
    def setUp(self):
        self.subject = CalendarDatesParser()
        self.reader = GtfsReader(ROOT_DIR, self.subject.filename)

    def test_calendar_dates_can_be_parsed(self):
        for each_line in self.reader:
            print each_line