from django.urls import path
from api.views import MergeTreesAPIView

urlpatterns = [
    path('merge/', MergeTreesAPIView.as_view(), name='merge_trees'),
]
