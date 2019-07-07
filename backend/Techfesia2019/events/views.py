from django.db import IntegrityError
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tags
from .permissions import IsStaffUser
from .serializers import TagsSerializer


class TagsListCreateView(APIView):
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


class TagsEditDeleteView(APIView):
    permission_classes = (IsStaffUser,)

    def put(self, request, name, format=None):
        try:
            tag = Tags.objects.get(name=name)
        except Tags.DoesNotExist:
            return Response({'error': 'Tag does not exist.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        tag.description = JSONParser().parse(request)['description']
        tag.save()
        return Response(TagsSerializer(tag).data, status=status.HTTP_202_ACCEPTED)


