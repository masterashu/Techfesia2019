from django.urls import path
from .views import TagsListCreateView, TagsEditDeleteView

urlpatterns = [
    path('tags', TagsListCreateView.as_view(), name='tags_list_create'),
    path('tags/<str:name>', TagsEditDeleteView.as_view(), name='tags_edit_delete'),
]
