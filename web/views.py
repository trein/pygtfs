from django.http import HttpResponse
from django.core import serializers
from service.models import Trip

import json


class JsonResponse(HttpResponse):
    def __init__(self, content, status=None):
        super(JsonResponse, self).__init__(
            content=content,
            status=status,
            mimetype='application/json',
            content_type='json',
        )

    @staticmethod
    def for_dict(content):
        content_as_json = json.dumps(content)
        return JsonResponse(content_as_json)

    @staticmethod
    def for_model(content):
        content_as_json = serializers.serialize('json', content)
        return JsonResponse(content_as_json)


def index(request):
    return JsonResponse.for_dict({"status": "ok"})


def bus_lines(request):
    return JsonResponse.for_model(Trip.objects.all()[:1])
