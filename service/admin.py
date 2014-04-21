from django.contrib.gis.admin import options
from django.contrib import admin
from service.models import Agency
from service.models import Zone
from service.models import Stop
from service.models import WheelchairAccessible
from service.models import RouteType
from service.models import Route
from service.models import Service
from service.models import Direction
from service.models import Block
from service.models import Shape
from service.models import Trip
from service.models import PickupType
from service.models import DropOffType
from service.models import StopTime
from service.models import Calendar
from service.models import ExceptionType
from service.models import CalendarDate
from service.models import Fare
from service.models import PaymentMethod
from service.models import FareAttribute
from service.models import FareRule
from service.models import Frequency
from service.models import Transfer

admin.site.register(Stop, options.OSMGeoAdmin)
admin.site.register(Shape, options.OSMGeoAdmin)
admin.site.register(Agency)
admin.site.register(Zone)
admin.site.register(RouteType)
admin.site.register(WheelchairAccessible)
admin.site.register(Route)
admin.site.register(Service)
admin.site.register(Direction)
admin.site.register(Block)
admin.site.register(Trip)
admin.site.register(PickupType)
admin.site.register(DropOffType)
admin.site.register(StopTime)
admin.site.register(Calendar)
admin.site.register(ExceptionType)
admin.site.register(CalendarDate)
admin.site.register(Fare)
admin.site.register(PaymentMethod)
admin.site.register(FareAttribute)
admin.site.register(FareRule)
admin.site.register(Frequency)
admin.site.register(Transfer)
