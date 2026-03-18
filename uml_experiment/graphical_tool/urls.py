from django.urls import path
from . import views

app_name = 'graphical_tool'

urlpatterns = [
    path('session/<int:assignment_id>/', views.graphical_interface, name='interface'),
    path('api/save-diagram/', views.save_diagram, name='save_diagram'),
    path('api/log-action/', views.log_action, name='log_action'),
    path('api/load-diagram/<str:session_id>/', views.load_diagram, name='load_diagram'),
]
