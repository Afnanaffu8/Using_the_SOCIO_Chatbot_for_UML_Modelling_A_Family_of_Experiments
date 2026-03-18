from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('performance/', views.performance_metrics, name='performance'),
    path('comparison/', views.tool_comparison, name='comparison'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
]
