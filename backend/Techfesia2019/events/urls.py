from django.urls import path
from .views import TagsDetailsView

urlpatterns = [
    path('tags', TagsDetailsView.as_view(), name='tags_details'),
]
