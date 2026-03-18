from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('admin/', include('adminpanel.urls')),
    path('tasks/', include('tasks.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('graphical/', include('graphical_tool.urls')),
    path('submissions/', include('submissions.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
