from rest_framework import serializers
from events.models import Tags, Category, Event, SoloEvent, TeamEvent


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['name', 'description']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']


class EventSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Event


class SoloEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = SoloEvent
        fields = ['public_id', 'event_picture', 'event_logo', 'title',
                  'description', 'start_date', 'start_time', 'end_date',
                  'end_time', 'venue', 'team_event', 'category', 'tags',
                  'max_participants', 'reserved_slots']
        depth = 2


class TeamEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamEvent
        fields = ['public_id', 'event_picture', 'event_logo', 'title',
                  'description', 'start_date', 'start_time', 'end_date',
                  'end_time', 'venue', 'team_event', 'min_team_size',
                  'max_team_size', 'category', 'tags',
                  'max_participants', 'reserved_slots']
        depth = 2
