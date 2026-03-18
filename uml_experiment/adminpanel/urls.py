from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/add/', views.add_participant, name='add_participant'),
    path('participants/<int:pk>/edit/', views.edit_participant, name='edit_participant'),
    path('participants/<int:pk>/delete/', views.delete_participant, name='delete_participant'),
    path('experiments/', views.experiment_config, name='experiment_config'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:pk>/edit/', views.edit_task, name='edit_task'),
    path('assignments/', views.assignment_management, name='assignment_management'),
    path('submissions/', views.submission_review, name='submission_review'),
    path('submissions/<int:pk>/evaluate/', views.evaluate_submission, name='evaluate_submission'),
]
