from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Tags
from .serializers import TagsSerializer


class TagsDetailsView(APIView):

    def get(self, request, format=None):
        tags = Tags.objects.all()
        serializer = TagsSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
