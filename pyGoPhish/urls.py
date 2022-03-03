"""PyGoPhish URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django Web Application Framework Imports
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

# pyGoPhish Pondering Application Imports
from pondering import views

# Microsoft Identity Web Imports
from ms_identity_web.django.msal_views_and_urls import MsalViews

msal_urls = MsalViews(settings.MS_IDENTITY_WEB).url_patterns()

urlpatterns = [
    path('', include('pondering.urls')),
    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    path('accounts/login/', admin.site.urls),
    path(f'{settings.AAD_CONFIG.django.auth_endpoints.prefix}/', include(msal_urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
