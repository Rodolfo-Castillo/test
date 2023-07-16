from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core import serializers
from django.utils import timezone
from zones.models import Zone
from zones.models import Distribution

@api_view(['POST'])
def add(request):
    print(request.data)
    zone_id = request.data.get('zone')
    percentage = request.data.get('percentage')
    Distribution.objects.create(percentage=percentage, zone=Zone.objects.get(pk=zone_id))
    x = serializers.serialize("json", Distribution.objects.all())
    return Response({'data':x,'msg':'Distribucion agregada, correctamente.'},status=status.HTTP_200_OK)


@api_view(['POST'])
def edit(request):
    zone_id = request.data.get('id')
    name = request.data.get('name')
    distributions = request.data.get('distributions')
    if Zone.objects.filter(name=name).count() < 2:
        zone = Zone.objects.filter(pk=zone_id).first()
        print (zone)
        if not zone:
            return Response('', status=status.HTTP_400_BAD_REQUEST)

        for distribution in distributions:
            distributionEdit = Distribution.objects.filter(id=distribution['id']).first()
            if not distributionEdit:
                return Response('', status=status.HTTP_400_BAD_REQUEST)
            distributionEdit.percentage = distribution['percentage']
            distributionEdit.save()
        
        if zone.name != name:
            zone.updated_at = timezone.now()
            zone.name = name
        zone.save()

        responseData={}
        responseData['name'] = zone.name
        responseData['distributions'] = []
        # use of range() to define a range of values
        values = range(len(distributions))
        for i in values:
            responseData['distributions'].append({"id":distributions[i]['id'],"percentage":distributions[i]['percentage']})
        print(responseData)
        return Response({'data':responseData,'msg':'Dato guardado con exito.'},status=status.HTTP_200_OK)
    else:
        return Response('Dato duplicado',status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def delete(request, id, zone):
    print(zone)
    distribution = Distribution.objects.filter(id=id).first()
    if not distribution:
        return Response('', status=status.HTTP_400_BAD_REQUEST)
    # instance = SomeModel.objects.get(id=id)
    distribution.delete()
    x = serializers.serialize("json", Distribution.objects.all())
    return Response({'data':x,'msg':'Distribucion eliminada con exito.'},status=status.HTTP_200_OK)