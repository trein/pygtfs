""" GTFS entities.

These are the entities returned by the various :py:mod:`pygtfs.schedule` lists.
Most of the attributes come directly from the gtfs reference. Also,
when possible relations are taken into account, e.g. a :py:class:`Route` class
has a `trips` attribute, with a list of trips for the specific route.

"""
from django.contrib.gis.db import models


class Agency(models.Model):
    """
    Model object representing an Agency (agency.txt).
    """

    """
    The agency_id field is an ID that uniquely identifies a transit agency.
    A transit feed may represent data from more than one agency. The agency_id
    is dataset unique. This field is optional for transit feeds that only contain
    data for a single agency.
    """
    agency_id = models.CharField(max_length=255, null=True, blank=True)

    """
    The agency_name field contains the full name of the transit agency.
    Google Maps will display this name.
    """
    name = models.TextField()

    """
    The agency_url field contains the URL of the transit agency
    """
    url = models.URLField()

    """
    The agency_timezone field contains the timezone where the transit
    agency is located. Timezone names never contain the space character
    but may contain an underscore. Please refer to
    http://en.wikipedia.org/wiki/List_of_tz_zones for a list of valid
    values. If multiple agencies are specified in the feed, each must
    have the same agency_timezone.
    """
    timezone = models.CharField(max_length=255)

    """ Optional
    The agency_lang field contains a two-letter ISO 639-1 code for the
    primary language used by this transit agency. The language code is
    case-insensitive (both en and EN are accepted). This setting defines
    capitalization rules and other language-specific settings for all
    text contained in this transit agency's feed. Please refer to
    http://www.loc.gov/standards/iso639-2/php/code_list.php for a
    list of valid values.
    """
    lang = models.CharField(max_length=2, null=True, blank=True)

    """ Optional
    The agency_phone field contains a single voice telephone number for
    the specified agency. This field is a string value that presents the
    telephone number as typical for the agency's service area. It can and
    should contain punctuation marks to group the digits of the number.
    Dialable text (for example, TriMet's "503-238-RIDE") is permitted,
    but the field must not contain any other descriptive text.
     """
    phone = models.CharField(max_length=255, null=True, blank=True)

    """ Optional
    The agency_fare_url specifies the URL of a web page that allows a
    rider to purchase tickets or other fare instruments for that agency online.
    """
    fare_url = models.URLField(null=True, blank=True)


class Zone(models.Model):
    """
    Define the fare zone.
    """
    zone_id = models.CharField(max_length=255, unique=True)


class Stop(models.Model):
    stop_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    url = models.URLField()
    desc = models.TextField(null=True, blank=True)
    geopoint = models.PointField(null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    zone = models.ForeignKey(Zone, null=True, blank=True)
    location_type = models.IntegerField(null=True,
                                        blank=True)  #TODO add choices for 0=blank=Stop and 1=Station
    parent_station = models.ForeignKey('self', null=True, blank=True)
    objects = models.GeoManager()


class RouteType(models.Model):
    """
    Referential data.
    """
    name = models.CharField(max_length=50)
    description = models.TextField()
    value = models.IntegerField(unique=True)


class Route(models.Model):
    """
    The route_id field contains an ID that uniquely identifies a route.
    The route_id is dataset unique.
    """
    route_id = models.CharField(max_length=255, unique=True)
    agency = models.ForeignKey(Agency, null=True, blank=True)

    """
    The route_short_name contains the short name of a route.
    This will often be a short, abstract identifier like "32",
    "100X", or "Green" that riders use to identify a route,
    but which doesn't give any indication of what places the
    route serves. If the route does not have a short name,
    please specify a route_long_name and use an empty string
    as the value for this field.
    """
    short_name = models.CharField(max_length=255)

    """
    The route_long_name contains the full name of a route.
    This name is generally more descriptive than the
    route_short_name and will often include the route's
    destination or stop. If the route does not have a
    long name, please specify a route_short_name and
    use an empty string as the value for this field.
    """
    long_name = models.TextField()

    """ Optional
    The route_desc field contains a description of a route.
    Please provide useful, quality information. Do not
    simply duplicate the name of the route. For example,
    "A trains operate between Inwood-207 St, Manhattan
    and Far Rockaway-Mott Avenue, Queens at all times.
    Also from about 6AM until about midnight, additional
    A trains operate between Inwood-207 St and Lefferts
    Boulevard (trains typically alternate between
    Lefferts Blvd and Far Rockaway)."
    """
    desc = models.TextField(null=True, blank=True)

    """
    The route_type field describes the type of transportation
    used on a route.
    """
    route_type = models.ForeignKey(RouteType)

    """ Optional
    The route_url field contains the URL of a web page
    about that particular route
    """
    url = models.URLField(null=True, blank=True)

    """ Optional
    In systems that have colors assigned to routes, the route_color field
    defines a color that corresponds to a route.
    """
    color = models.CharField(max_length=6, default="FFFFFF")

    """
    The route_text_color field can be used to
    specify a legible color to use
    for text drawn against a background of route_color
    """
    text_color = models.CharField(max_length=6, default="000000")


class Service(models.Model):
    service_id = models.CharField(max_length=255, unique=True)


class Direction(models.Model):
    """
    Referential data.
    """
    name = models.CharField(max_length=20)
    value = models.IntegerField(unique=True)


class Block(models.Model):
    block_id = models.CharField(max_length=255, unique=True)


class Shape(models.Model):
    """
    Model object represeting a Shape (shapes.txt).
    """
    
    shape_id = models.CharField(max_length=255)
    geopoint = models.PointField()

    """
    The shape_pt_sequence field associates the latitude
    and longitude of a shape point with its sequence
    order along the shape. The values for
    shape_pt_sequence must be non-negative integers,
    and they must increase along the trip.

    For example, if the shape "A_shp" has three points
    in its definition, the shapes.txt file might contain
    these rows to define the shape:

    A_shp,37.61956,-122.48161,0
    A_shp,37.64430,-122.41070,6
    A_shp,37.65863,-122.30839,11
    """
    pt_sequence = models.IntegerField()
    dist_traveled = models.FloatField(null=True, blank=True)
    objects = models.GeoManager()



class Trip(models.Model):
    route = models.ForeignKey(Route)
    service = models.ForeignKey(Service)
    trip_id = models.CharField(max_length=255, unique=True)
    headsign = models.TextField(null=True, blank=True)
    direction = models.ForeignKey(Direction, null=True, blank=True)
    block = models.ForeignKey(Block, null=True, blank=True)
    shape_id = models.CharField(max_length=255, null=True, blank=True)


class PickupType(models.Model):
    """Referential data"""
    name = models.CharField(max_length=255)
    value = models.IntegerField()


class DropOffType(models.Model):
    """Referential data"""
    name = models.CharField(max_length=255)
    value = models.IntegerField()


class StopTime(models.Model):
    trip = models.ForeignKey(Trip)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    stop = models.ForeignKey(Stop)
    stop_sequence = models.IntegerField()
    headsign = models.TextField(null=True, blank=True)
    pickup_type = models.ForeignKey(PickupType, null=True, blank=True)
    drop_off_type = models.ForeignKey(DropOffType, null=True, blank=True)
    shape_dist_traveled = models.FloatField(null=True, blank=True)


class Calendar(models.Model):
    """
    Model object representing a service entry (calendar.txt).
    """

    """
    The service_id contains an ID that uniquely identifies a
    set of dates when service is available for one or
    more routes.
    """
    service = models.ForeignKey(Service)

    """
    The monday field contains a binary value that indicates 
    whether the service is valid for all Mondays.
    """
    monday = models.IntegerField()
    tuesday = models.IntegerField()
    wednesday = models.IntegerField()
    thursday = models.IntegerField()
    friday = models.IntegerField()
    saturday = models.IntegerField()
    sunday = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()


class ExceptionType(models.Model):
    """Referential data"""
    name = models.CharField(max_length=255)
    value = models.IntegerField()


class CalendarDate(models.Model):
    service = models.ForeignKey(Service)
    date = models.DateField()
    exception_type = models.ForeignKey(ExceptionType)


class Fare(models.Model):
    fare_id = models.CharField(max_length=255, unique=True)


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    vale = models.IntegerField()


class FareAttribute(models.Model):
    fare = models.ForeignKey(Fare)
    price = models.FloatField()
    currency = models.CharField(max_length=3)
    payment_method = models.ForeignKey(PaymentMethod)
    transfers = models.IntegerField(null=True, blank=True)
    transfer_duration = models.IntegerField(null=True,
                                            blank=True)  # duration in seconds


class FareRule(models.Model):
    fare = models.ForeignKey(Fare)
    route = models.ForeignKey(Route, null=True, blank=True)
    origin = models.ForeignKey(Zone, null=True, blank=True,
                               related_name="origin")
    destination = models.ForeignKey(Zone, null=True, blank=True,
                                    related_name="destination")
    contains = models.ForeignKey(Zone, null=True, blank=True,
                                 related_name="contains")


class Frequency(models.Model):
    trip = models.ForeignKey(Trip)
    start_time = models.TimeField()
    end_time = models.TimeField()
    headway_secs = models.IntegerField()
    exact_times = models.IntegerField(null=True, blank=True)


class Transfer(models.Model):
    from_stop = models.ForeignKey(Stop, related_name="from_stop")
    to_stop = models.ForeignKey(Stop, related_name="to_stop")
    transfer_type = models.IntegerField()
    min_transfer_time = models.IntegerField(null=True, blank=True)