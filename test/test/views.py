import json

from django.shortcuts import render

from zones.api.serializers import ZoneSerializer
from zones.api.serializers import DistributionSerializer
from zones.models import Zone
from zones.models import Distribution


def home(request):
    zones_data = ZoneSerializer(Zone.objects.all(), many=True).data
    distributions_data = DistributionSerializer(Distribution.objects.all(), many=True).data
    
    json_context = {
        'zones': zones_data,
        'distributions':distributions_data
    }

    context = {
        'context_json': json.dumps(json_context)
    }

    return render(request, 'home.html', context)
