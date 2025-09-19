from django.urls import path
from . import views

urlpatterns = [
    path('', views.conflict_report_home),
]