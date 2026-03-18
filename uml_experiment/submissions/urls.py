from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('submit/<int:assignment_id>/', views.submit_diagram, name='submit'),
    path('feedback/<int:submission_id>/', views.submit_feedback, name='feedback'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('<int:pk>/', views.submission_detail, name='detail'),
]
