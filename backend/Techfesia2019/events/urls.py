from django.urls import path
from .views import TagsListCreateView, TagsEditDeleteView, CategoryListCreateView, \
    CategoryEditDeleteView, EventListCreateView, EventDetailEditDeleteView, EventPictureLogoUploadView

urlpatterns = [
    path('', EventListCreateView.as_view(), name='events_list_create'),
    path('/tags', TagsListCreateView.as_view(), name='tags_list_create'),
    path('/tags/<str:name>', TagsEditDeleteView.as_view(), name='tags_edit_delete'),
    path('/category', CategoryListCreateView.as_view(), name='category_list_create'),
    path('/category/<str:name>', CategoryEditDeleteView.as_view(), name='category_edit_delete'),
    path('/<str:public_id>', EventDetailEditDeleteView.as_view(), name='events_delete'),
    path('/<str:public_id>/photo', EventPictureLogoUploadView.as_view(), name='upload event_picture event_logo'),
]
