from rest_framework import serializers
from events.models import Tags, Category


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['name', 'description']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']