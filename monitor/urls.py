from django.urls import path
from . import views
from .views import MonitorListView

urlpatterns = [
    path('api/list', MonitorListView.as_view()),
]