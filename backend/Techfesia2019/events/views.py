from django.db import IntegrityError
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tags
from .permissions import IsStaffUser
from .serializers import TagsSerializer


class TagsDetailsView(APIView):
    permission_classes = (IsStaffUser,)

    def get(self, request, format=None):
        tags = Tags.objects.all()
        serializer = TagsSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        try:
            tag = Tags.objects.create(name=data['name'], description=data['description'])
        except IntegrityError:
            return Response({'error': 'Tag already exist.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        data = TagsSerializer(tag).data
        return Response(data, status=status.HTTP_201_CREATED)

