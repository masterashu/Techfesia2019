from rest_framework import serializers
from events.models import Tags, Category, SoloEvent, TeamEvent
from events.image_models import ImageUploadModel
from . import path_resolvers


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


class EventPictureLogoUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageUploadModel
        fields = ('event', 'uploaded_picture', 'uploaded_logo')

    def create(self, validated_data):
        img = ImageUploadModel(
            purpose="event_picture and event_logo upload",
            event=validated_data['event'],
            upload_picture_path=path_resolvers.resolve_event_picture_path(validated_data['event']),
            upload_logo_path=path_resolvers.resolve_event_logo_path(validated_data['event']),
            uploaded_picture=validated_data['uploaded_picture'],
            uploaded_logo=validated_data['uploaded_logo'],
        )
        img.save()
        return img

    def update(self, instance, validated_data):
        raise NotImplementedError("update is not allowed on this serializer. "
                                  "For purpose of logging, every file upload must happen in a new serializer")
