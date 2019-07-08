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
    name = serializers.CharField(source='title', read_only=True)
    category = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Event
        fields = ['public_id', 'event_picture', 'event_logo', 'name',
                  'description', 'start_date', 'start_time', 'end_date',
                  'end_time', 'venue', 'team_event', 'category', 'tags',
                  'max_participants', 'reserved_slots']


class SoloEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoloEvent
        fields = '__all__'
        depth = 2


class TeamEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamEvent
        fields = '__all__'
        depth = 2
