from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('session/<int:assignment_id>/', views.chatbot_interface, name='interface'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/save-diagram/', views.save_diagram, name='save_diagram'),
    path('api/get-history/<int:session_id>/', views.get_chat_history, name='get_history'),
]
