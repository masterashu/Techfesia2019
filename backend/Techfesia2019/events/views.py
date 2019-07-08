from django.db import IntegrityError
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tags, Category, Event, SoloEvent, TeamEvent
from .permissions import IsStaffUser
from .serializers import TagsSerializer, CategorySerializer, EventSerializer, SoloEventSerializer, TeamEventSerializer
import datetime


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

    def delete(self, request, name, format=None):
        try:
            tag = Tags.objects.get(name=name)
            if tag.events.count() > 0:
                return Response({'error': 'Cant delete a tag that is in use.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            tag.delete()
        except Tags.DoesNotExist:
            return Response({'error': 'This tag does not exist.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreateView(APIView):
    permission_classes = (IsStaffUser,)

    def get(self, request, format=None):
        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        try:
            category = Category.objects.create(name=data['name'], description=data['description'])
        except IntegrityError:
            return Response({'error': 'This category already exist.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        data = CategorySerializer(category).data
        return Response(data, status=status.HTTP_201_CREATED)


class CategoryEditDeleteView(APIView):
    permission_classes = (IsStaffUser,)

    def put(self, request, name, format=None):
        try:
            category = Category.objects.get(name=name)
        except Category.DoesNotExist:
            return Response({'error': 'Category does not exist.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        category.description = JSONParser().parse(request)['description']
        category.save()
        return Response(CategorySerializer(category).data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, name, format=None):
        try:
            category = Category.objects.get(name=name)
            if category.events.count() > 0:
                return Response({'error': 'Cant delete a category that is in use.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            category.delete()
        except Category.DoesNotExist:
            return Response({'error': 'This category does not exist.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventListCreateView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        solo_events = SoloEvent.objects.all()
        solo_events_serializer = SoloEventSerializer(solo_events, many=True)
        team_events = TeamEvent.objects.all()
        team_events_serializer = TeamEventSerializer(team_events, many=True)
        return Response({'events': solo_events_serializer.data + team_events_serializer.data},
                        status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data = JSONParser().parse(request)

        # 1. Validating dates
        try:
            datetime.datetime.strptime(data['start_date'], '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'Incorrect start_date format, should be "YYYY-MM-DD" or Invalid start_date'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            datetime.datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'Incorrect end_date format, should be "YYYY-MM-DD" or Invalid end_date'},
                            status=status.HTTP_400_BAD_REQUEST)

        # 2. Validating time
        try:
            datetime.datetime.strptime(data['start_time'], '%H:%M')
        except ValueError:
            return Response({'error': 'Incorrect start_time format, should be "HH:MM" or Invalid start_date'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            datetime.datetime.strptime(data['end_time'], '%H:%M')
        except ValueError:
            return Response({'error': 'Incorrect end_time format, should be "HH:MM" or Invalid end_time'},
                            status=status.HTTP_400_BAD_REQUEST)

        # 3. Checking date and time
        if data['end_date'] < data['start_date']:
            return Response({'error': 'end_date can not be before than start_date of event'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif data['end_date'] == data['start_date']:
            if data['end_time'] <= data['start_time']:
                return Response({'error': 'end_time can not be before than start_time of event'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 4. Checking max_participants and reserved_slots
        if data['reserved_slots'] > data['max_participants']:
            return Response({'error': 'reserved_slots cannot be greater than max_participants'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 5. Validating list of categories and tags
        category_list = list()
        invalid_category_list = list()
        for name in data['category']:
            try:
                category_list.append(Category.objects.get(name=name))
            except Category.DoesNotExist:
                invalid_category_list.append(name)

        tags_list = list()
        invalid_tags_list = list()
        for name in data['tags']:
            try:
                tags_list.append(Tags.objects.get(name=name))
            except Tags.DoesNotExist:
                invalid_tags_list.append(name)

        if len(invalid_category_list) > 0 and len(invalid_tags_list) == 0:
            return Response({'error': f'The following categories {invalid_category_list} do not exist.'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        elif len(invalid_category_list) == 0 and len(invalid_tags_list) > 0:
            return Response({'error': f'The following tags {invalid_tags_list} do not exist.'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        elif len(invalid_category_list) > 0 and len(invalid_tags_list) > 0:
            return Response({'error': f'The following categories {invalid_category_list}'
                            f' and tags {invalid_tags_list} do not exist.'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 6. Creating event on behalf of team_event parameter
        if data['team_event']:
            try:
                team_event = TeamEvent(event_picture=data['event_picture'], event_logo=data['event_logo'],
                                       title=data['name'], description=data['description'],
                                       start_time=data['start_time'], start_date=data['start_date'],
                                       end_date=data['end_date'], end_time=data['end_time'], venue=data['venue'],
                                       team_event=data['team_event'],  min_team_size=data['min_team_size'],
                                       max_team_size=data['max_team_size'],
                                       max_participants=data['max_participants'], reserved_slots=data['reserved_slots'])
                team_event.save()
            except IntegrityError:
                return Response({'error': 'Team event with such name already exists'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            team_event.category.set(category_list)
            team_event.tags.set(tags_list)
            team_event.save()
            data = TeamEventSerializer(team_event).data
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            try:
                solo_event = SoloEvent(event_picture=data['event_picture'], event_logo=data['event_logo'],
                                       title=data['name'], description=data['description'],
                                       start_time=data['start_time'], start_date=data['start_date'],
                                       end_date=data['end_date'], end_time=data['end_time'], venue=data['venue'],
                                       team_event=data['team_event'],
                                       max_participants=data['max_participants'],
                                       reserved_slots=data['reserved_slots'])
                solo_event.save()
            except IntegrityError:
                return Response({'error': 'Solo event with such name already exists'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            solo_event.category.set(category_list)
            solo_event.tags.set(tags_list)
            solo_event.save()
            data = SoloEventSerializer(solo_event).data
            return Response(data, status=status.HTTP_201_CREATED)
