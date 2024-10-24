# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Train
from .serializers import TrainSerializer, TrainWithTicketClassSerializer

class TrainListView(APIView):
    def get(self, request):
        trains = Train.objects.all()
        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TrainDetailView(APIView):
    def get(self, request, id):
        try:
            train = Train.objects.get(pk=id)
            serializer = TrainWithTicketClassSerializer(train)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Train.DoesNotExist:
            return Response({'detail': 'Train not found.'}, status=status.HTTP_404_NOT_FOUND)
