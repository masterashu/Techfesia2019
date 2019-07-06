from rest_framework import serializers
from events.models import Tags


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['name', 'description']
