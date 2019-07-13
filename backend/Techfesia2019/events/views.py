import os
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tags, Category, Event, SoloEvent, TeamEvent
from .permissions import IsStaffUser
from .serializers import TagsSerializer, CategorySerializer, SoloEventSerializer, TeamEventSerializer,\
    EventPictureLogoUploadSerializer
from .path_resolvers import resolve_event_data_folder
import datetime
from Techfesia2019.settings import BASE_DIR


def validation_errors(data):

    # 1. Validating dates
    try:
        datetime.datetime.strptime(data['start_date'], '%Y-%m-%d')
    except ValueError:
        return [1, Response({'error': 'Incorrect start_date format, should be "YYYY-MM-DD" or Invalid start_date'},
                            status=status.HTTP_400_BAD_REQUEST)]
    try:
        datetime.datetime.strptime(data['end_date'], '%Y-%m-%d')
    except ValueError:
        return [1, Response({'error': 'Incorrect end_date format, should be "YYYY-MM-DD" or Invalid end_date'},
                            status=status.HTTP_400_BAD_REQUEST)]

    # 2. Validating time
    try:
        datetime.datetime.strptime(data['start_time'], '%H:%M')
    except ValueError:
        return [1, Response({'error': 'Incorrect start_time format, should be "HH:MM" or Invalid start_time'},
                            status=status.HTTP_400_BAD_REQUEST)]
    try:
        datetime.datetime.strptime(data['end_time'], '%H:%M')
    except ValueError:
        return [1, Response({'error': 'Incorrect end_time format, should be "HH:MM" or Invalid end_time'},
                            status=status.HTTP_400_BAD_REQUEST)]

    # 3. Checking date and time
    if data['end_date'] < data['start_date']:
        return [1, Response({'error': 'end_date can not be before than start_date of event'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)]
    elif data['end_date'] == data['start_date']:
        if data['end_time'] <= data['start_time']:
            return [1, Response({'error': 'end_time can not be before than start_time of event'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)]
    # 4. Checking max_participants and reserved_slots
    if data['reserved_slots'] > data['max_participants']:
        return [1, Response({'error': 'reserved_slots cannot be greater than max_participants'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)]

    # 5. Validating list of categories and tags
    category_list = list()
    has_tags = 0
    tags_list = list()
    if 'category' in data:
        invalid_category_list = list()
        for name in data['category']:
            try:
                category_list.append(Category.objects.get(name=name))
            except Category.DoesNotExist:
                invalid_category_list.append(name)
        if len(invalid_category_list) > 0:
            return [1, Response({'error': f'The following categories {invalid_category_list} do not exist.'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)]
        if len(category_list) == 0:
            try:
                category_list.append(Category.objects.get(name='Others'))
            except Category.DoesNotExist:
                c = Category(name='Others',
                             description='It is a default category for events')
                c.save()
                category_list.append(Category.objects.get(name='Others'))
    else:
        try:
            category_list.append(Category.objects.get(name='Others'))
        except Category.DoesNotExist:
            c = Category(name='Others',
                         description='It is a default category for events')
            c.save()
            category_list.append(Category.objects.get(name='Others'))

    if 'tags' in data:
        has_tags = 1
        invalid_tags_list = list()
        for name in data['tags']:
            try:
                tags_list.append(Tags.objects.get(name=name))
            except Tags.DoesNotExist:
                invalid_tags_list.append(name)
        if len(invalid_tags_list) > 0:
            return [1, Response({'error': f'The following tags {invalid_tags_list} do not exist.'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)]

    if has_tags == 0:
        return [2, category_list]
    if has_tags == 1:
        return [3, category_list, tags_list]


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
        if name == 'Others':
            return Response({'error': 'It is a default category for events.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            category = Category.objects.get(name=name)
            if category.events.count() > 0:
                return Response({'error': 'Cant delete a category that is in use.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            category.delete()
        except Category.DoesNotExist:
            return Response({'error': 'This category does not exist.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventListCreateView(APIView):
    permission_classes = (IsAuthenticated, IsStaffUser, )

    def get(self, request, format=None):
        solo_events = SoloEvent.objects.all()
        team_events = TeamEvent.objects.all()

        # implementing filtering
        data = dict(request.query_params.lists())
        if 'category' in data:
            for c in data['category']:
                solo_events = SoloEvent.objects.filter(category__name=c) & solo_events
                team_events = TeamEvent.objects.filter(category__name=c) & team_events

        if 'tags' in data:
            for t in data['tags']:
                solo_events = SoloEvent.objects.filter(tags__name=t) & solo_events
                team_events = TeamEvent.objects.filter(tags__name=t) & team_events

        solo_events_serializer = SoloEventSerializer(solo_events, many=True)
        team_events_serializer = TeamEventSerializer(team_events, many=True)
        return Response({'events': solo_events_serializer.data + team_events_serializer.data},
                        status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        error_list = validation_errors(data)

        has_tags = 0
        tags_list = list()
        if error_list[0] == 1:
            return error_list[1]
        elif error_list[0] == 2:
            category_list = error_list[1]
        else:
            category_list = error_list[1]
            tags_list = error_list[2]
            has_tags = 1

        no_solo_team_event = 0
        # Checking if public_id is provided, then unique.
        if 'public_id' in data:
            try:
                SoloEvent.objects.get(public_id=data['public_id'])
                return Response({'error': 'Solo event with such public_id already exists'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            except SoloEvent.DoesNotExist:
                try:
                    TeamEvent.objects.get(public_id=data['public_id'])
                    return Response({'error': 'Team event with such public_id already exists'},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                except TeamEvent.DoesNotExist:
                    no_solo_team_event = 1

        # checking if it is a team_event
        if data['team_event']:
            try:
                SoloEvent.objects.get(title=data['title'])
                return Response({'error': 'Solo event with such title already exists.'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            except SoloEvent.DoesNotExist:
                if 'min_team_size' in data and 'max_team_size' in data:
                    if data['max_team_size'] < data['min_team_size']:
                        return Response({'error': 'max_team_size can not be less than min_team_size'},
                                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    try:
                        team_event = TeamEvent(event_picture=data['event_picture'], event_logo=data['event_logo'],
                                               title=data['title'], description=data['description'],
                                               start_time=data['start_time'], start_date=data['start_date'],
                                               end_date=data['end_date'], end_time=data['end_time'], venue=data['venue'],
                                               team_event=data['team_event'], min_team_size=data['min_team_size'],
                                               max_team_size=data['max_team_size'],
                                               max_participants=data['max_participants'],
                                               reserved_slots=data['reserved_slots'])
                        if no_solo_team_event == 1:
                            team_event.public_id = data['public_id']
                        team_event.save()
                    except IntegrityError:
                        return Response({'error': 'Team event with such title already exists'},
                                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                    team_event.category.set(category_list)
                    if has_tags == 1:
                        team_event.tags.set(tags_list)
                    team_event.save()
                    data = TeamEventSerializer(team_event).data
                    return Response(data, status=status.HTTP_201_CREATED)
                return Response({'error': 'min_team_size and max_team_size parameters are not provided'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        else:
            try:
                TeamEvent.objects.get(title=data['title'])
                return Response({'error': 'Team Event with such title already exists.'},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            except TeamEvent.DoesNotExist:
                try:
                    solo_event = SoloEvent(event_picture=data['event_picture'], event_logo=data['event_logo'],
                                           title=data['title'], description=data['description'],
                                           start_time=data['start_time'], start_date=data['start_date'],
                                           end_date=data['end_date'], end_time=data['end_time'], venue=data['venue'],
                                           team_event=data['team_event'],
                                           max_participants=data['max_participants'],
                                           reserved_slots=data['reserved_slots'])
                    if no_solo_team_event == 1:
                        solo_event.public_id = data['public_id']
                    solo_event.save()
                except IntegrityError:
                    return Response({'error': 'Solo event with such title already exists'},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                solo_event.category.set(category_list)
                if has_tags == 1:
                    solo_event.tags.set(tags_list)
                solo_event.save()
                data = SoloEventSerializer(solo_event).data
                return Response(data, status=status.HTTP_201_CREATED)


class EventDetailEditDeleteView(APIView):
    permission_classes = (IsStaffUser, )

    def get(self, request, public_id, format=None):
        try:
            solo_event = SoloEvent.objects.get(public_id=public_id)
            solo_event_serializer = SoloEventSerializer(solo_event)
        except SoloEvent.DoesNotExist:
            try:
                team_event = TeamEvent.objects.get(public_id=public_id)
                team_event_serializer = TeamEventSerializer(team_event)
            except TeamEvent.DoesNotExist:
                return Response({'error': 'This event does not exist'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return Response(team_event_serializer.data, status=status.HTTP_200_OK)
        return Response(solo_event_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, public_id, format=None):
        try:
            solo_event = SoloEvent.objects.get(public_id=public_id)
            data = JSONParser().parse(request)
            if 'public_id' in data:
                if public_id != data['public_id']:
                    return Response({'error': 'public_id of an event can not be changed'},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            error_list = validation_errors(data)
            has_tags = 0
            tags_list = list()
            if error_list[0] == 1:
                return error_list[1]
            elif error_list[0] == 2:
                category_list = error_list[1]
            else:
                category_list = error_list[1]
                tags_list = error_list[2]
                has_tags = 1

            # Shifting to team event
            if data['team_event']:
                if 'min_team_size' in data and 'max_team_size' in data:
                    if data['max_team_size'] < data['min_team_size']:
                        return Response({'error': 'max_team_size can not be less than min_team_size'},
                                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                    try:  # if title is changed
                        TeamEvent.objects.get(title=data['title'])
                        return Response({'error': 'Team event with such title already exists.'},
                                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    except TeamEvent.DoesNotExist:
                        team_event = TeamEvent(event_picture=data['event_picture'], event_logo=data['event_logo'],
                                               title=data['title'], description=data['description'],
                                               start_time=data['start_time'], start_date=data['start_date'],
                                               end_date=data['end_date'], end_time=data['end_time'],
                                               venue=data['venue'], team_event=data['team_event'],
                                               min_team_size=data['min_team_size'], max_team_size=data['max_team_size'],
                                               max_participants=data['max_participants'], public_id=public_id,
                                               reserved_slots=data['reserved_slots'])
                        solo_event.delete()
                        team_event.save()
                        team_event.category.set(category_list)
                        if has_tags == 1:
                            team_event.tags.set(tags_list)
                        team_event.save()
                        team_event_serializer = TeamEventSerializer(team_event)
                        return Response(team_event_serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'error': 'min_team_size and max_team_size parameters are not provided'},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                solo_event_serializer = SoloEventSerializer(solo_event, data=data)
                if solo_event_serializer.is_valid():
                    solo_event_serializer.save()
                    solo_event.category.set(category_list)
                    if has_tags == 1:
                        solo_event.tags.set(tags_list)
                    else:  # removing previous tags
                        for tag in solo_event.tags.all():
                            solo_event.tags.remove(tag)
                    solo_event.save()
                    return Response(solo_event_serializer.data, status=status.HTTP_202_ACCEPTED)
                return Response(solo_event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except SoloEvent.DoesNotExist:
            try:
                team_event = TeamEvent.objects.get(public_id=public_id)
                data = JSONParser().parse(request)
                if 'public_id' in data:
                    if public_id != data['public_id']:
                        return Response({'error': 'public_id of an event can not be changed'},
                                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                error_list = validation_errors(data)
                has_tags = 0
                tags_list = list()
                if error_list[0] == 1:
                    return error_list[1]
                elif error_list[0] == 2:
                    category_list = error_list[1]
                else:
                    category_list = error_list[1]
                    tags_list = error_list[2]
                    has_tags = 1

                # Shifting to solo event
                if not data['team_event']:
                    try:  # if title is changed
                        SoloEvent.objects.get(title=data['title'])
                        return Response({'error': 'Solo event with such title already exists.'},
                                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    except SoloEvent.DoesNotExist:
                        solo_event = SoloEvent(event_picture=data['event_picture'], event_logo=data['event_logo'],
                                               title=data['title'], description=data['description'],
                                               start_time=data['start_time'], start_date=data['start_date'],
                                               end_date=data['end_date'], end_time=data['end_time'],
                                               venue=data['venue'], team_event=data['team_event'],
                                               max_participants=data['max_participants'], public_id=public_id,
                                               reserved_slots=data['reserved_slots'])
                        team_event.delete()
                        solo_event.save()
                        solo_event.category.set(category_list)
                        if has_tags == 1:
                            solo_event.tags.set(tags_list)
                        solo_event.save()
                        solo_event_serializer = SoloEventSerializer(solo_event)
                        return Response(solo_event_serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    team_event_serializer = TeamEventSerializer(team_event, data=data)
                    if team_event_serializer.is_valid():
                        team_event_serializer.save()
                        team_event.category.set(category_list)
                        if has_tags == 1:
                            team_event.tags.set(tags_list)
                        else:  # removing previous tags
                            for tag in team_event.tags.set():
                                team_event.tags.remove(tag)
                        team_event.save()
                        return Response(team_event_serializer.data, status=status.HTTP_202_ACCEPTED)
                    return Response(team_event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except TeamEvent.DoesNotExist:
                return Response({'error': 'This event does not exist'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, public_id, format=None):
        try:
            event = Event.objects.get(public_id=public_id)
            os.system(f'rm -rf {BASE_DIR}/media/events/{event.public_id}/')
            event.delete()
        except Event.DoesNotExist:
            return Response({'error': 'This event does not exist'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(status=status.HTTP_200_OK)


class EventPictureLogoUploadView(APIView):
    permission_classes = (IsStaffUser,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, public_id):
        event = get_object_or_404(Event, public_id=public_id)
        modified_data_dict = {
            'uploaded_picture': request.data.get('picture'),
            'uploaded_logo': request.data.get('logo'),
            'event': event.pk
        }
        sr = EventPictureLogoUploadSerializer(data=modified_data_dict)
        if sr.is_valid():
            img = sr.save()

            event.event_picture = img.uploaded_picture.url
            event.event_logo = img.uploaded_logo.url
            event.save()
            return Response(data={"event_picture": event.event_picture, "event_logo": event.event_logo},
                            status=status.HTTP_201_CREATED)

        return Response(sr.errors)

