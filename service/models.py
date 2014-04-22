""" GTFS entities.

These are the entities returned by the various :py:mod:`pygtfs.schedule` lists.
Most of the attributes come directly from the gtfs reference. Also,
when possible relations are taken into account, e.g. a :py:class:`Route` class
has a `trips` attribute, with a list of trips for the specific route.

"""
from django.contrib.gis.db import models


class GtfsModel(models.Model):
    def update_param(self, param, value):
        setattr(self, param, value)


class WheelchairAccessible(GtfsModel):
    """Referential data"""

    # wheelchair_accessible Optional:
    #
    # 0 (or empty) - indicates that there is no accessibility information
    # for the trip
    # 1 - indicates that the vehicle being used on this particular trip can
    # accommodate at least one rider in a wheelchair
    # 2 - indicates that no riders in wheelchairs can be accommodated on
    # this trip
    value = models.IntegerField()
    name = models.CharField(max_length=255)


class Agency(GtfsModel):
    # agency_id Optional:
    # The agency_id field is an ID that uniquely identifies a transit agency. A
    # transit feed may represent data from more than one agency. The agency_id
    # is data set unique. This field is optional for transit feeds that only
    # contain data for a single agency.
    agency_id = models.CharField(max_length=255, null=True, blank=True)

    # agency_name Required:
    # The agency_name field contains the full name of the transit agency.
    # Google Maps will display this name.
    name = models.TextField()

    # agency_url Required:
    # The agency_url field contains the URL of the transit agency. The value
    # must be a fully qualified URL that includes  http:// or https://,
    # and any special characters in the URL must be correctly escaped.
    #
    # See http://www.w3.org/Addressing/URL/4_URI_Recommentations.html
    # for a description of how to create fully qualified URL values.
    url = models.URLField()

    # agency_timezone Required:
    # The agency_timezone field contains the timezone where the transit
    # agency is located. Timezone names never contain the space character
    # but may contain an underscore.
    #
    # Please refer to http://en.wikipedia .org/wiki/List_of_tz_zones for a
    # list of valid values. If multiple agencies are specified in the feed,
    # each must have the same agency_timezone.
    timezone = models.CharField(max_length=255)

    # agency_lang Optional:
    # The agency_lang field contains a two-letter ISO 639-1 code for the
    # primary language used by this transit agency. The language code is
    # case-insensitive (both en and EN are accepted). This setting defines
    # capitalization rules  other language-specific settings for all text
    # contained in this transit agency's feed.
    #
    # Please refer to http://www.loc.gov/standards/iso639-2/php/code_list.php
    # for a list of valid values.
    lang = models.CharField(max_length=2, null=True, blank=True)

    # agency_phone Optional:
    # The agency_phone field contains a single voice telephone number for
    # the specified agency. This field is a string value that presents the
    # telephone number as typical for the agency's service area. It can and
    # should contain punctuation marks to group the digits of the number.
    # Dialable text (for example, TriMet's "503-238-RIDE") is permitted,
    # but the field must not contain any other descriptive text.
    phone = models.CharField(max_length=255, null=True, blank=True)

    # agency_fare_url Optional:
    # The agency_fare_url specifies the URL of a web  page that allows a
    # rider to purchase tickets or other fare instruments for that agency
    # online. The value must be a fully qualified  URL that includes http://
    # or https://, and any special characters in the URL must be correctly
    # escaped.
    #
    # See http://www.w3.org/Addressing/URL/4_URI_Recommentations.html for a
    # description of how to create fully qualified URL values.
    fare_url = models.URLField(null=True, blank=True)

    def __eq__(self, other):
        return other.name == self.name and \
               other.agency_id == self.agency_id and \
               other.url == self.url and \
               other.timezone == self.timezone and \
               other.lang == self.lang and \
               other.phone == self.phone and \
               other.fare_url == self.fare_url


class Zone(GtfsModel):
    # zone_id Optional:
    # The zone_id field defines the fare zone for a stop ID. Zone IDs are
    # required if you want to provide fare information using fare_rules.txt.
    # If this stop ID represents a station, the zone ID is ignored.
    zone_id = models.CharField(max_length=255, unique=True)


class Stop(GtfsModel):
    # stop_id Required:
    # The stop_id field contains an ID that uniquely identifies a stop or
    # station. Multiple routes may use the same stop. The stop_id is dataset
    # unique.
    stop_id = models.CharField(max_length=255, unique=True)

    # stop_code Optional:
    # The stop_code field contains short text or a number that uniquely
    # identifies the stop for passengers. Stop codes are often used in
    # phone-based transit information systems or printed on stop signage to
    # make it easier for riders to get a stop schedule or real-time arrival
    # information for a particular stop. The stop_code field should only be
    # used for stop codes that are displayed to passengers. For internal codes,
    # use stop_id. This field should be left blank for stops without a code.
    code = models.CharField(max_length=255, null=True, blank=True)

    # stop_name Required:
    # The stop_name field contains the name of a stop or station. Please use a
    # name that people will understand in the local and tourist vernacular.
    name = models.CharField(max_length=255)

    # stop_url Optional:
    # The stop_url field contains the URL of a web page about a particular stop.
    # This should be different from the agency_url and the route_url fields.
    # The value must be a fully qualified URL that includes http:// or
    # https://, and any special characters in the URL must be correctly
    # escaped.
    #
    # See http://www.w3.org/Addressing/URL/4_URI_Recommentations.html
    # for a description of how to create fully qualified URL values.
    url = models.URLField(null=True, blank=True)

    # stop_desc Optional:
    # The stop_desc field contains a description of a stop. Please provide
    # useful, quality information. Do not simply duplicate the name of the stop.
    desc = models.TextField(null=True, blank=True)

    # zone_id Optional:
    # The zone_id field defines the fare zone for a stop ID. Zone IDs are
    # required  if you want to provide fare information using fare_rules.txt.
    # If this stop ID represents a station, the zone ID is ignored.
    zone = models.ForeignKey(Zone, null=True, blank=True)

    # location_type Optional:
    # The location_type field identifies whether this stop ID represents a
    # stop or station. If no location type is specified, or the location_type
    #  is blank, stop IDs are treated as stops. Stations may have different
    # properties from stops when they are represented on a map or used in
    # trip planning.
    location_type = models.IntegerField(null=True, blank=True)

    # parent_station Optional:
    # For stops that are physically located inside stations, the parent_station
    # field identifies the station associated with the stop. To use this field,
    # stops.txt must also contain a row where this stop ID is assigned
    # location type=1.
    parent_station = models.ForeignKey('self', null=True, blank=True)

    # stop_timezone Optional:
    # The stop_timezone field contains the timezone in which this stop or
    # station is located. Please refer to Wikipedia List of Timezones for a
    # list of valid values.  If omitted, the stop should be assumed to be
    # located in the timezone specified by agency_timezone in agency.txt.
    #
    # When a stop has a parent station, the stop is considered to be in the
    # timezone specified by the parent station's stop_timezone value. If the
    # parent has no stop_timezone value, the stops  that belong to that
    # station are assumed to be in the timezone specified by agency_timezone,
    # even if the stops have their own stop_timezone values. In other words,
    # if a given stop has a parent_station value, any stop_timezone value
    # specified for that stop must be ignored.
    #
    # Even if stop_timezone values are provided in stops.txt, the times in
    # stop_times.txt should continue to be specified as time since midnight
    # in the timezone specified by agency_timezone in agency.txt. This
    # ensures that the time values in a trip always increase over the course of
    # a trip, regardless of which timezones the trip crosses.
    # timezone =  models.CharField(max_length=255, null=True, blank=True)

    # wheelchair_boarding Optional:
    # The wheelchair_boarding field identifies whether wheelchair boardings
    # are possible from the specified stop or station. The field can have the
    # following values:
    #
    # 0 (or empty) - indicates that there is no accessibility information for
    # the stop
    # 1 - indicates that at least some vehicles at this stop can be boarded
    # by a rider in a wheelchair
    # 2 - wheelchair boarding is not possible at this stop
    #
    # When a stop is part of a larger station complex, as indicated by a
    # stop with a parent_station value, the stop's wheelchair_boarding field
    # has the following additional semantics:
    #
    # 0 (or empty) - the stop will inherit its wheelchair_boarding value from
    # the parent station, if specified in the parent
    # 1 - there exists some accessible path from outside the station to the
    # specific stop / platform
    # 2 - there exists no accessible path from outside the station to the
    # specific stop / platform
    wheelchair = models.ForeignKey(WheelchairAccessible, null=True, blank=True)

    geopoint = models.PointField(null=True, blank=True)
    objects = models.GeoManager()

    def __eq__(self, other):
        return other.stop_id == self.stop_id and \
               other.code == self.code and \
               other.name == self.name and \
               other.url == self.url and \
               other.desc == self.desc and \
               other.zone == self.zone and \
               other.location_type == self.location_type and \
               other.parent_station == self.parent_station and \
               other.wheelchair == self.wheelchair and \
               other.geopoint == self.geopoint


class RouteType(GtfsModel):
    # route_type Required:
    # The route_type field describes the type of transportation used on a
    # route. Valid values for this field are:
    #
    # 0 - Tram, Streetcar, Light rail. Any light rail or street level system
    # within a metropolitan area.
    # 1 - Subway, Metro. Any underground rail system within a metropolitan area.
    # 2 - Rail. Used for intercity or long-distance travel.
    # 3 - Bus. Used for short- and long-distance bus routes.
    # 4 - Ferry. Used for short- and long-distance boat service.
    # 5 - Cable car. Used for street-level cable cars where the cable runs
    # beneath the car.
    # 6 - Gondola, Suspended cable car. Typically used for aerial cable cars
    # where the car is suspended from the cable.
    # 7 - Funicular. Any rail system designed for steep inclines.
    name = models.CharField(max_length=50)
    description = models.TextField()
    value = models.IntegerField(unique=True)


class Route(GtfsModel):
    # route_id Required:
    # The route_id field contains an ID that uniquely identifies a route. The
    # route_id is dataset unique.
    route_id = models.CharField(max_length=255, unique=True)

    # agency_id Optional:
    # The agency_id field defines an agency for the specified route. This value
    # is referenced from the agency.txt file. Use this field when you are
    # providing data for routes from more than one agency.
    agency = models.ForeignKey(Agency, null=True, blank=True)

    # route_short_name Required:
    # The route_short_name contains the short name of a route. This will
    # often be a short, abstract identifier like "32", "100X", or "Green"
    # that riders use to identify a route, but which doesn't give any
    # indication of what places the route serves. At  least one of route
    # short_name or route_long_name must be specified, or potentially both if
    # appropriate. If the route does not have a short name, please specify a
    # route_long_name and use an empty string as the value for this field.
    # See a Google Maps screenshot highlighting the route_short_name.
    short_name = models.CharField(max_length=255)

    # route_long_name Required:
    # The route_long_name contains the full name of a route. This name is
    # generally more descriptive than the route_short_name and will often
    # include the route's destination or stop. At least one of
    # route_short_name or route_long_name must be specified, or potentially
    # both if appropriate. If the route does not have a long name, please
    # specify a route_short_name and use an empty string as the value for
    # this field. See a Google Maps screenshot highlighting the route_long_name.
    long_name = models.TextField()

    # route_desc Optional:
    # The route_desc field contains a description of a route. Please provide
    # useful, quality information. Do not simply duplicate the name of the
    # route. For example,
    #
    # A trains operate between Inwood-207 St, Manhattan and Far Rockaway-Mott
    # Avenue, Queens at all times. Also from about 6AM until about midnight,
    # additional A trains operate between Inwood-207 St and Lefferts
    # Boulevard (trains typically alternate between Lefferts Blvd and Far
    # Rockaway).
    desc = models.TextField(null=True, blank=True)

    # route_type Required:
    # The route_type field describes the type of transportation used on a
    # route. Valid values for this field are:
    #
    # 0 - Tram, Streetcar, Light rail. Any light rail or street level system
    # within a metropolitan area.
    # 1 - Subway, Metro. Any underground rail system within a metropolitan area.
    # 2 - Rail. Used for intercity or long-distance travel.
    # 3 - Bus. Used for short- and long-distance bus routes.
    # 4 - Ferry. Used for short- and long-distance boat service.
    # 5 - Cable car. Used for street-level cable cars where the cable runs
    # beneath the car.
    # 6 - Gondola, Suspended cable car. Typically used for aerial cable cars
    # where the car is suspended from the cable.
    # 7 - Funicular. Any rail system designed for steep inclines.
    route_type = models.ForeignKey(RouteType)

    # route_url Optional:
    # The route_url field contains the URL of a web page about that particular
    # route. This should be different from the agency_url. The value must be a
    # fully qualified URL that includes http:// or https://, and any special
    # characters in the URL must be correctly  escaped.
    #
    # See http://www.w3.org/Addressing/URL/4_URI_Recommentations.html for a
    # description of how to create fully qualified URL values.
    url = models.URLField(null=True, blank=True)

    # route_color Optional:
    # In systems that have colors assigned to routes, the route_color field
    # defines a color that corresponds to a route. The color must be provided
    # as a six-character hexadecimal number, for example, 00FFFF. If no color
    #  is specified, the default route color is  white (FFFFFF). The color
    # difference between route_color and route_text_color should provide
    # sufficient contrast when viewed on a black and white screen. The W3C
    # Techniques for Accessibility Evaluation And Repair Tools document
    # offers a useful algorithm for evaluating  color contrast. There are
    # also helpful online tools for choosing contrasting colors, including
    # the snook.ca Color Contrast Check application.
    color = models.CharField(max_length=6, default="FFFFFF")

    # route_text_color Optional:
    # The route_text_color field can be used to specify a legible color
    # to use for text drawn against a background of route_color. The color
    # must be provided as a six-character hexadecimal number, for example,
    # FFD700. If no color is specified, the default  text color is black (
    # 000000). The color difference between route_color and route_text_color
    #  should provide sufficient contrast when viewed on a black and white
    # screen.
    text_color = models.CharField(max_length=6, default="000000")

    def __eq__(self, other):
        return other.route_id == self.route_id and \
               other.agency == self.agency and \
               other.short_name == self.short_name and \
               other.long_name == self.long_name and \
               other.desc == self.desc and \
               other.route_type == self.route_type and \
               other.url == self.url and \
               other.color == self.color and \
               other.text_color == self.text_color


class Service(GtfsModel):
    # service_id Required:
    # The service_id contains an ID that uniquely identifies a set of dates
    # when service is available for one or more routes. This value is
    # referenced from the calendar.txt or calendar_dates.txt file.
    service_id = models.CharField(max_length=255, unique=True)


class Direction(GtfsModel):
    # direction_id Optional:
    # The direction_id field contains a binary value that indicates the
    # direction of travel for a trip. Use this field to distinguish between
    # bi-directional trips with the same route_id. This field is not used in
    # routing; it provides a way to separate  trips by direction when
    # publishing time tables. You can specify names for each direction with
    # the trip_headsign field
    #
    # It provides a way to separate trips by direction when publishing time
    # tables. You can specify names for each direction with the
    # trip_headsign field.
    #
    # 0 - travel in one direction (e.g. outbound travel)
    # 1 - travel in the opposite direction (e.g. inbound travel)
    #
    # For example, you could use the trip_headsign and direction_id fields
    # together to assign a name to travel in each direction for a set of
    # trips. A trips.txt file could contain these rows for use in time tables:
    #
    # trip_id,...,trip_headsign,direction_id
    # 1234,...,to Airport,0
    # 1505,...,to Downtown,1
    name = models.CharField(max_length=20)
    value = models.IntegerField(unique=True)


class Block(GtfsModel):
    # block_id Optional:
    # The block_id field identifies the block to which the trip belongs. A block
    # consists of two or more sequential trips made using the same vehicle,
    # where a passenger can transfer from one trip to the next just by
    # staying in the vehicle. The block_id must be referenced by two or more
    # trips in trips.txt.
    block_id = models.CharField(max_length=255, unique=True)


class Shape(GtfsModel):
    # shape_id Required:
    # The shape_id field contains an ID that uniquely identifies a shape.
    shape_id = models.CharField(max_length=255)

    # shape_pt_sequence Required:
    # The shape_pt_sequence field associates the latitude and longitude
    # of a shape point with its sequence order along the shape. The values
    # for shape_pt_sequence  must be non-negative integers, and they must
    # increase along the trip. For example, if the  shape "A_shp" has three
    # points in its definition, the shapes.txt file might contain these rows
    # to define the shape:
    #
    # A_shp,37.61956,-122.48161,0
    # A_shp,37.64430,-122.41070,6
    # A_shp,37.65863,-122.30839,11
    pt_sequence = models.IntegerField()

    # shape_dist_traveled Optional:
    # When used in the shapes.txt file, the shape_dist_traveled field
    # positions a shape point as a distance traveled along a shape from the
    # first shape point. The shape_dist_traveled field represents a real
    # distance traveled along the route in units such as feet or kilometers.
    # This information allows the trip planner to determine how much of the
    # shape to draw when showing part of a trip on the map. The values used
    # for shape_dist_traveled must increase along with shape_pt_sequence:
    # they cannot be used to show reverse travel along a route. The units
    # used for shape_dist_traveled in the shapes.txt file must match the
    # units that are used for this field in the stop_times.txt file. For
    # example, if a bus travels along the three points defined above for
    # A_shp, the additional shape_dist_traveled values (shown  here in
    # kilometers) would look like this:
    #
    # A_shp,37.61956,-122.48161,0,0
    # A_shp,37.64430,-122.41070,6,6.8310
    # A_shp,37.65863,-122.30839,11,15.8765
    dist_traveled = models.FloatField(null=True, blank=True)

    # shape_pt_lat Required:
    # The shape_pt_lat field associates a shape point's latitude with a shape
    # ID. The field value must be a valid WGS 84 latitude. Each row in
    # shapes.txt represents a shape point in your shape definition. For
    # example, if the shape "A_shp" has three points in  its definition,
    # the shapes.txt file might contain these rows to define the shape:
    #
    # shape_pt_lon Required The shape_pt_lon field associates a shape point's
    # longitude with a shape ID. The field value must be a valid WGS 84
    # longitude value from -180 to 180. Each row in shapes.txt represents a
    # shape point in your shape definition. For example, if the shape
    # "A_shp" has three points in its definition, the shapes.txt file might
    # contain these rows to  define the shape:
    #
    # A_shp,37.61956,-122.48161,0
    # A_shp,37.64430,-122.41070,6
    # A_shp,37.65863,-122.30839,11
    geopoint = models.PointField()
    objects = models.GeoManager()

    def __eq__(self, other):
        return other.shape_id == self.shape_id and \
               other.geopoint == self.geopoint and \
               other.pt_sequence == self.pt_sequence and \
               other.dist_traveled == self.dist_traveled


class Trip(GtfsModel):
    # trip_id Required:
    # The trip_id field contains an ID that identifies a trip. The trip_id is
    # dataset unique.
    trip_id = models.CharField(max_length=255, unique=True)

    # route_id Required:
    # The route_id field contains an ID that uniquely identifies a route. This
    # value is referenced from the routes.txt file.
    route = models.ForeignKey(Route)

    # service_id Required:
    # The service_id contains an ID that uniquely identifies a set of dates
    # when service is available for one or more routes. This value is
    # referenced from the calendar.txt or calendar_dates.txt file.
    service = models.ForeignKey(Service)

    # trip_headsign Optional:
    # The trip_headsign field contains the text that appears on a sign that
    # identifies the trip's destination to passengers. Use this field to
    # distinguish between different patterns of service in the same route. If
    # the headsign changes during a trip, you can override the trip_headsign
    # by specifying values for the the stop_headsign field in stop_times.txt.
    #  See a Google Maps screenshot highlighting the headsign.
    headsign = models.TextField(null=True, blank=True)

    # direction_id Optional:
    # The direction_id field contains a binary value that indicates the
    # direction of travel for a trip. Use this field to distinguish between
    # bi-directional trips with the same route_id. This field is not used in
    # routing; it provides a way to separate trips by direction when
    # publishing time tables. You can specify names for each direction with
    # the trip_headsign field.
    #
    # It provides a way to separate trips by direction when publishing time
    # tables. You can specify names for each direction with the trip_headsign
    # field.
    #
    # 0 - travel in one direction (e.g. outbound travel)
    # 1 - travel in the opposite direction (e.g. inbound travel)
    #
    # For example, you could use the trip_headsign and direction_id fields
    # together to assign a name to travel in each direction for a set of
    # trips. A trips.txt file could contain these rows for use in time tables:
    #
    # trip_id,...,trip_headsign,direction_id
    # 1234,...,to Airport,0
    # 1505,...,to Downtown,1
    direction = models.ForeignKey(Direction, null=True, blank=True)

    # block_id Optional:
    # The block_id field identifies the block to which the trip belongs. A block
    # consists of two or more sequential trips made using the same vehicle,
    # where a passenger can transfer from one trip to the next just by
    # staying in the vehicle. The block_id must be referenced by two or more
    # trips in trips.txt.
    block = models.ForeignKey(Block, null=True, blank=True)

    # shape_id Optional:
    # The shape_id field contains an ID that defines a shape for the trip. This
    # value is referenced from the shapes.txt file. The shapes.txt file allows
    # you to define how a line should be drawn on the map to represent a trip.
    shapes = models.ManyToManyField(Shape, null=True, blank=True)

    # wheelchair_accessible Optional:
    #
    # 0 (or empty) - indicates that there is no accessibility information
    # for the trip
    # 1 - indicates that the vehicle being used on this particular trip can
    # accommodate at least one rider in a wheelchair
    # 2 - indicates that no riders in wheelchairs can be accommodated on
    # this trip
    wheelchair = models.ForeignKey(WheelchairAccessible, null=True, blank=True)

    # trip_short_name Optional:
    # The trip_short_name field contains the text that appears in
    # schedules and sign boards to identify the trip to passengers, for
    # example, to identify train numbers for commuter rail trips. If riders
    # do not commonly rely on trip names, please leave this field blank. A
    # trip_short_name value, if provided, should uniquely identify a trip
    # within a service day; it should not be used for destination names or
    # limited/express  designations.
    short_name = models.CharField(max_length=255, null=True, blank=True)

    def __eq__(self, other):
        # it does not compare shapes
        # other.shapes == self.shapes and \
        return other.trip_id == self.trip_id and \
               other.route == self.route and \
               other.headsign == self.headsign and \
               other.service == self.service and \
               other.direction == self.direction and \
               other.block == self.block and \
               other.wheelchair == self.wheelchair and \
               other.short_name == self.short_name


class PickupType(GtfsModel):
    """Referential data"""
    name = models.CharField(max_length=255)
    value = models.IntegerField()


class DropOffType(GtfsModel):
    """Referential data"""
    name = models.CharField(max_length=255)
    value = models.IntegerField()


class StopTime(GtfsModel):
    # trip_id Required:
    # The trip_id field contains an ID that identifies a trip. This value is
    # referenced from the trips.txt file.
    trip = models.ForeignKey(Trip)

    # arrival_time Required:
    # The arrival_time specifies the arrival time at a specific stop for a
    # specific trip on a route. The time is measured from "noon minus 12h"
    # (effectively midnight, except for days on which daylight savings time
    # changes occur) at the beginning of the service date. For times
    # occurring after midnight on the service date, enter the time as a value
    # greater than 24:00:00 in HH:MM:SS local time for the day on which the
    # trip schedule begins. If you don't have separate times for arrival and
    # departure at a stop, enter the same value for arrival_time and
    # departure_time. If this stop isn't a time point, use an empty string
    # value for the arrival_time and departure_time fields. Stops without
    # arrival times will be scheduled based on the nearest preceding timed
    # stop. To ensure accurate routing, please provide arrival and departure
    # times for all stops that are time points. Do not interpolate stops. You
    # must specify arrival and departure times for the first and last stops in
    # a trip. Times must be eight digits in HH:MM:SS format (H:MM:SS is also
    # accepted, if the hour begins with 0). Do not pad times with spaces. The
    # following columns list stop times for a trip and the proper way to
    # express those times in the arrival_time field:
    #
    # Time          arrival_time value
    # 08:10:00 A.M. 08:10:00 or 8:10:00
    # 01:05:00 P.M. 13:05:00
    # 07:40:00 P.M. 19:40:00
    # 01:55:00 A.M. 25:55:00
    #
    # Note: Trips that span multiple dates will have stop times greater than
    # 24:00:00. For example, if a trip begins at 10:30:00 p.m. and ends at
    # 2:15:00 a.m. on the following day, the stop times would be 22:30:00 and
    #  26:15:00. Entering those stop times as 22:30:00 and 02:15:00
    # would not produce the desired results.
    arrival_time = models.TimeField()

    # departure_time Required:
    # The departure_time specifies the departure time from a specific stop
    # for a specific trip on a route. The time is measured from "noon minus
    # 12h" (effectively midnight, except for days on which daylight savings
    # time changes occur) at the beginning of the service date. For times
    # occurring after midnight on the service date, enter the time as a value
    # greater than 24:00:00 in HH:MM:SS local time for the day on which the
    # trip schedule begins. If you don't have separate times for arrival and
    # departure at a stop, enter the same value for arrival_time and
    # departure_time. If this stop isn't a time point, use an empty string
    # value for the arrival_time and departure_time fields. Stops without
    # arrival times will be scheduled based on the nearest preceding timed
    # stop. To ensure accurate routing, please provide arrival and departure
    # times for all stops that are time points. Do not interpolate stops. You
    # must specify arrival and departure times for the first and last stops
    # in a trip. Times must be eight digits in HH:MM:SS format (H:MM:SS is
    # also accepted, if the hour begins with 0). Do not pad times with spaces.
    # The following columns list stop times for a trip and the proper way to
    # express those times in the departure_time field:
    #
    # Time            departure_time value
    # 08:10:00 A.M.   08:10:00 or 8:10:00
    # 01:05:00 P.M.   13:05:00
    # 07:40:00 P.M.   19:40:00
    # 01:55:00 A.M.   25:55:00
    #
    # Note: Trips that span multiple dates will have stop times greater
    # than 24:00:00. For example, if a trip begins at 10:30:00 p.m. and ends
    # at 2:15:00 a.m. on the following day, the stop times would be 22:30:00
    # and 26:15:00. Entering those stop times as 22:30:00 and 02:15:00
    # would not produce the desired results.
    departure_time = models.TimeField()

    # stop_id Required:
    # The stop_id field contains an ID that uniquely identifies a stop. Multiple
    # routes may use the same stop. The stop_id is referenced from the stops.txt
    # file. If location_type is used in stops.txt, all stops referenced in
    # stop_times.txt must have location_type of 0. Where possible, stop_id
    # values should remain consistent between feed updates. In other words,
    # stop A with stop_id 1 should have stop_id 1 in all subsequent data
    # updates. If a stop is not a time point, enter blank values for arrival
    # time and departure_time.
    stop = models.ForeignKey(Stop)

    # stop_sequence Required:
    # The stop_sequence field identifies the order of the stops for a
    # particular trip. The values for stop_sequence must be non-negative
    # integers, and they must increase along the trip. For example, the first
    # stop on the trip could have a stop_sequence of 1, the second stop on
    # the trip could have a stop_sequence of 23, the third stop could have
    # a stop_sequence of 40, and so on.
    stop_sequence = models.IntegerField()

    # stop_headsign Optional:
    # The stop_headsign field contains the text that appears on a sign that
    # identifies the trip's destination to passengers. Use this field to
    # override the default trip_headsign when the headsign changes between
    # stops. If this headsign is associated with an  entire trip,
    # use trip_headsign instead. See a Google Maps screenshot highlighting the
    # headsign.
    headsign = models.TextField(null=True, blank=True)

    # pickup_type Optional:
    # The pickup_type field indicates whether passengers are picked up at a
    # stop as part of the normal schedule or whether a pickup at the stop is
    # not available. This field also allows the transit agency to indicate
    # that passengers must call the agency or notify the driver to arrange a
    # pickup at a particular stop. Valid values for this field are:
    #
    # 0 - Regularly scheduled pickup
    # 1 - No pickup available
    # 2 - Must phone agency to arrange pickup
    # 3 - Must coordinate with driver to arrange pickup
    #
    # The default value for this field is 0.
    pickup_type = models.ForeignKey(PickupType, null=True, blank=True)

    # drop_off_type Optional:
    # The drop_off_type field indicates whether passengers are dropped off
    # at a stop as part of the normal schedule or whether a drop off at the
    # stop is not available. This field also allows the transit agency to
    # indicate that passengers must call the agency or notify the driver to
    # arrange a drop off at a particular stop. Valid values for this field
    # are:
    #
    # 0 - Regularly scheduled drop off
    # 1 - No drop off available
    # 2 - Must phone agency to arrange drop off
    # 3 - Must coordinate with driver to arrange drop off
    #
    # The default value for this field is 0.
    drop_off_type = models.ForeignKey(DropOffType, null=True, blank=True)

    # shape_dist_traveled Optional:
    # When used in the stop_times.txt file, the shape_dist_traveled
    # field positions a stop as a distance from the first shape point. The
    # shape_dist_traveled field represents a real distance traveled along the
    # route in units such as feet or kilometers. For example, if a bus
    # travels a distance of 5.25 kilometers from the start of the shape to
    # the stop, the shape_dist_traveled for the stop ID would be entered as
    # "5.25". This information allows the trip planner to determine how much
    # of the shape to draw when showing part of a trip on the map. The values
    # used for shape_dist_traveled must increase along with stop_sequence:
    # they cannot be used to show reverse travel along a route. The units used
    # for shape_dist_traveled in the stop_times.txt file must match the units
    # that are used for this field in the shapes.txt file.
    shape_dist_traveled = models.FloatField(null=True, blank=True)

    def __eq__(self, other):
        return other.trip == self.trip and \
               other.arrival_time == self.arrival_time and \
               other.departure_time == self.departure_time and \
               other.stop == self.stop and \
               other.stop_sequence == self.stop_sequence and \
               other.headsign == self.headsign and \
               other.drop_off_type == self.drop_off_type and \
               other.pickup_type == self.pickup_type and \
               other.shape_dist_traveled == self.shape_dist_traveled


class Calendar(GtfsModel):
    # service_id Required:
    # The service_id contains an ID that uniquely identifies a set of dates
    # when service is available for one or more routes. Each service_id value
    # can appear at most once in a calendar.txt file. This value is dataset
    # unique. It is referenced by the trips.txt file.
    service = models.ForeignKey(Service)

    # weekday Required:
    # The weekday field contains a binary value that indicates is valid for
    # the weekday.
    #
    # A value of 1 indicates that service is available for all weekday in the
    # date range. (The date range is specified using the start_date and end
    # date fields.)
    #
    # A value of 0 indicates that service is not available on weekday in the
    # date range.
    #
    # Note: You may list exceptions for particular dates, such as holidays,
    # in the calendar_dates.txt file.
    monday = models.IntegerField()
    tuesday = models.IntegerField()
    wednesday = models.IntegerField()
    thursday = models.IntegerField()
    friday = models.IntegerField()
    saturday = models.IntegerField()
    sunday = models.IntegerField()

    # start_date Required:
    # The start_date field contains the start date for the service. The
    # start_date field's value should be in YYYYMMDD format.
    start_date = models.DateField()

    # end_date Required:
    # The end_date field contains the end date for the service. This date is
    # included in the service interval. The end_date field's value should be in
    # YYYYMMDD format.
    end_date = models.DateField()

    def __eq__(self, other):
        return other.service == self.service and \
               other.monday == self.monday and \
               other.tuesday == self.tuesday and \
               other.wednesday == self.wednesday and \
               other.thursday == self.thursday and \
               other.friday == self.friday and \
               other.saturday == self.saturday and \
               other.sunday == self.sunday and \
               other.start_date == self.start_date and \
               other.end_date == self.end_date


class ExceptionType(GtfsModel):
    """Referential data"""
    name = models.CharField(max_length=255)
    value = models.IntegerField()


class CalendarDate(GtfsModel):
    # service_id Required:
    # The service_id contains an ID that uniquely identifies a set of dates
    # when a service exception is available for one or more routes. Each
    # (service_id, date) pair can only appear once in calendar_dates.txt. If
    # the a service_id value appears in both the calendar.txt and
    # calendar_dates.txt files, the information in calendar_dates.txt
    # modifies the service information specified in calendar.txt. This field
    # is referenced by the trips.txt file.
    service = models.ForeignKey(Service)

    # date Required:
    # The date field specifies a particular date when service availability is
    # different than the norm. You can use the exception_type field to indicate
    # whether service is available on the specified date. The date field's
    # value should be in YYYYMMDD format.
    date = models.DateField()

    # exception_type Required:
    # The exception_type indicates whether service is available on the date
    # specified in the date field.
    #
    # A value of 1 indicates that service has been added for the
    # specified date.

    # A value of 2 indicates that service has been removed for the
    # specified date.
    #
    # For example, suppose a route has one set of trips available on holidays
    # and another set of trips available on all other days. You could have
    # one service_id that corresponds to the regular service schedule and
    # another service_id that corresponds to the holiday schedule. For a
    # particular holiday, you would use the calendar_dates.txt file to add
    # the holiday to the holiday service_id and to remove the holiday from
    # the regular service_id schedule.
    exception_type = models.ForeignKey(ExceptionType)

    def __eq__(self, other):
        return other.service == self.service and \
               other.date == self.date and \
               other.exception_type == self.exception_type


class Fare(GtfsModel):
    fare_id = models.CharField(max_length=255, unique=True)


class PaymentMethod(GtfsModel):
    name = models.CharField(max_length=50)
    vale = models.IntegerField()


class FareAttribute(GtfsModel):
    # fare_id Required:
    # The fare_id field contains an ID that uniquely identifies a fare class.
    # The fare_id is dataset unique.
    fare = models.ForeignKey(Fare)

    # price Required:
    # The price field contains the fare price, in the unit specified by
    # currency_type.
    price = models.FloatField()

    # currency_type Required:
    # The currency_type field defines the currency used to pay the fare.
    # Please use the ISO 4217 alphabetical currency codes which can be found
    # at the following URL: http://www.iso.org/iso/home/standards/iso4217.htm.
    currency = models.CharField(max_length=3)

    # payment_method Required:
    # The payment_method field indicates when the fare must be paid. Valid
    # values for this field are:
    #
    # 0 - Fare is paid on board.
    # 1 - Fare must be paid before boarding.
    payment_method = models.ForeignKey(PaymentMethod)

    # transfers Required:
    # The transfers field specifies the number of transfers permitted on this
    # fare. Valid values for this field are:
    #
    # 0 - No transfers permitted on this fare.
    # 1 - Passenger may transfer once.
    # 2 - Passenger may transfer twice.
    # (empty) - If this field is empty, unlimited transfers are permitted.
    transfers = models.IntegerField(null=True, blank=True)

    # transfer_duration Optional:
    # The transfer_duration field specifies the length of time in
    # seconds before a transfer expires. When used with a transfers value of 0,
    # the transfer_duration field indicates how long a ticket is valid for a
    # fare where no transfers are allowed. Unless you intend to use this
    # field to indicate ticket validity, transfer_duration should be omitted
    # or empty when transfers is set to 0.
    transfer_duration = models.IntegerField(null=True, blank=True)


class FareRule(GtfsModel):
    # fare_id Required:
    # The fare_id field contains an ID that uniquely identifies a fare class.
    # This value is referenced from the fare_attributes.txt file.
    fare = models.ForeignKey(Fare)

    # route_id Optional:
    # The route_id field associates the fare ID with a route. Route IDs are
    # referenced from the routes.txt file. If you have several routes with the
    # same fare attributes, create a row in fare_rules.txt for each route.
    # For example, if fare class "b" is valid on route "TSW" and "TSE",
    # the fare_rules.txt file would contain these rows for the fare class:
    #
    # b,TSW
    # b,TSE
    route = models.ForeignKey(Route, null=True, blank=True)

    # origin_id Optional:
    # The origin_id field associates the fare ID with an origin zone ID. Zone
    # IDs are referenced from the stops.txt file. If you have several origin
    # IDs with the same fare attributes, create a row in fare_rules.txt for
    # each origin ID. For example, if fare class "b" is valid for all travel
    # originating from either zone "2" or zone "8", the fare_rules.txt file
    # would contain these rows for the fare class:
    #
    # b, , 2
    # b, , 8
    origin = models.ForeignKey(Zone, null=True, blank=True,
                               related_name="origin")

    # destination_id Optional:
    # The destination_id field associates the fare ID with a destination
    # zone ID. Zone IDs are referenced from the stops.txt file. If you have
    # several destination IDs with the same fare attributes, create a row in
    # fare_rules.txt for each destination ID. For example, you could use the
    # origin_ID and destination_ID fields together to specify that fare class
    # "b" is valid for travel between zones 3 and 4, and for travel between
    # zones 3 and 5, the fare_rules.txt file would contain these rows for the
    # fare class:
    #
    # b, , 3,4
    # b, , 3,5
    destination = models.ForeignKey(Zone, null=True, blank=True,
                                    related_name="destination")

    # contains_id Optional:
    # The contains_id field associates the fare ID with a zone ID, referenced
    # from the stops.txt file. The fare ID is then associated with itineraries
    # that pass through every contains_id zone. For example, if fare class
    # "c" is associated with all travel on the GRT route that passes through
    # zones 5, 6, and 7 the fare_rules.txt would contain these rows:
    #
    # c,GRT,,,5
    # c,GRT,,,6
    # c,GRT,,,7
    #
    # Because all contains_id zones must be matched for the fare to apply, an
    # itinerary that passes through zones 5 and 6 but not zone 7 would not
    # have fare class "c". For more detail, see FareExamples in the
    # GoogleTransitDataFeed project wiki.
    contains = models.ForeignKey(Zone, null=True, blank=True,
                                 related_name="contains")


class Frequency(GtfsModel):
    # trip_id Required:
    # The trip_id contains an ID that identifies a trip on which the specified
    # frequency of service applies. Trip IDs are referenced from the trips.txt
    # file.
    trip = models.ForeignKey(Trip)

    # start_time Required:
    # The start_time field specifies the time at which service begins with the
    # specified frequency. The time is measured from "noon minus 12h"
    # (effectively midnight, except for days on which daylight savings time
    # changes occur) at the beginning of the service date. For times
    # occurring after midnight, enter the time as a value greater than
    # 24:00:00 in HH:MM:SS local time for the day on which the trip schedule
    # begins. E.g. 25:35:00.
    start_time = models.TimeField()

    # end_time Required:
    # The end_time field indicates the time at which service changes to a
    # different frequency (or ceases) at the first stop in the trip. The time
    # is measured from "noon minus 12h" (effectively midnight, except for
    # days on which daylight savings time changes occur) at the beginning of
    # the service date. For times occurring after midnight, enter the time as
    # a value greater than 24:00:00 in HH:MM:SS local time for the day on which
    # the trip schedule begins. E.g. 25:35:00.
    end_time = models.TimeField()

    # headway_secs Required:
    # The headway_secs field indicates the time between departures from the
    # same stop (headway) for this trip type, during the time interval
    # specified by start_time and end_time. The headway value must be entered
    # in seconds. Periods in which headways are defined (the rows in
    # frequencies.txt) shouldn't overlap for the same trip, since it's hard to
    # determine what should be inferred from two overlapping headways.
    # However, a headway period may begin at the exact same time that another
    # one ends, for instance:
    #
    # A, 05:00:00, 07:00:00, 600
    # B, 07:00:00, 12:00:00, 1200
    headway_secs = models.IntegerField()

    # exact_times Optional:
    # The exact_times field determines if frequency-based trips should be
    # exactly scheduled based on the specified headway information. Valid
    # values for this field are:
    #
    # 0 or (empty) - Frequency-based trips are not exactly scheduled. This is
    # the default behavior.
    #
    # 1 - Frequency-based trips are exactly scheduled. For a frequencies.txt
    # row, trips are scheduled starting with
    # trip_start_time = start_time + xheadway_secs for all x in (0, 1, 2, ...)
    # where trip_start_time < end_time.
    #
    # The value of exact_times must be the same for all frequencies.txt rows
    # with the same trip_id. If exact_times is 1 and a frequencies.txt row
    # has a start_time equal to end_time, no trip must be scheduled. When
    # exact_times is 1, care must be taken to choose an end_time value that
    # is greater than the last desired trip start time but less than the last
    # desired trip start time + headway_secs.
    exact_times = models.IntegerField(null=True, blank=True)


class Transfer(GtfsModel):
    # from_stop_id Required:
    # The from_stop_id field contains a stop ID that identifies a stop or
    # station where a connection between routes begins. Stop IDs are referenced
    # from the stops.txt file. If the stop ID refers to a station that
    # contains multiple stops, this transfer rule applies to all stops in
    # that station.
    from_stop = models.ForeignKey(Stop, related_name="from_stop")

    # to_stop_id Required:
    # The to_stop_id field contains a stop ID that identifies a stop or station
    # where a connection between routes ends. Stop IDs are referenced from the
    # stops.txt file. If the stop ID refers to a station that contains
    # multiple stops, this transfer rule applies to all stops in that station.
    to_stop = models.ForeignKey(Stop, related_name="to_stop")

    # transfer_type Required:
    # The transfer_type field specifies the type of connection for the
    # specified (from_stop_id, to_stop_id) pair. Valid values for this field
    # are:
    #
    # 0 or (empty) - This is a recommended transfer point between two routes.
    #
    # 1 - This is a timed transfer point between two routes. The departing
    # vehicle is expected to wait for the arriving one, with sufficient time
    # for a passenger to transfer between routes.
    #
    # 2 - This transfer requires a minimum amount of time between arrival and
    # departure to ensure a connection. The time required to transfer is
    # specified by min_transfer_time.
    #
    # 3 - Transfers are not possible between routes at this location.
    transfer_type = models.IntegerField()

    # min_transfer_time Optional:
    # When a connection between routes requires an amount of time between
    # arrival and departure (transfer_type=2), the min_transfer_time field
    # defines the amount of time that must be available in an itinerary to
    # permit a transfer between routes at these stops. The min_transfer_time
    # must be sufficient to permit a typical rider to move between the two
    # stops, including buffer time to allow for schedule variance on each
    # route. The min_transfer_time value must be entered in seconds,
    # and must be a non-negative integer.
    min_transfer_time = models.IntegerField(null=True, blank=True)