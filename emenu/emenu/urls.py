import debug_toolbar

from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('card/', include('card.urls'), name='card'),
    path('api/', include('card.api_urls'), name='api'),
    path('api-auth/', include('rest_framework.urls')),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', RedirectView.as_view(pattern_name='card-list'), name='home'),
    path('__debug__', include(debug_toolbar.urls)),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
]
