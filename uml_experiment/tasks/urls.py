from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/start/', views.start_task, name='start_task'),
]
