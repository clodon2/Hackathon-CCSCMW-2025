from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_select, name="select_student"),
    path('schedule/', views.student_scheduler, name="schedule"),
    path('select/<int:pk>/', views.set_student_session, name='selected_student'),
    path('progress/', views.student_progress, name="progress")
]