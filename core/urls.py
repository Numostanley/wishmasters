"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.versioning import get_api_version

public_urls = [
    path('admin/', admin.site.urls),
    path('users/', include('apis.users.urls')),
    path('contest/', include('apis.contest.urls')),

]

api_version: str = get_api_version(settings.API_VERSIONS, 'v1')

if settings.API_PREFIX:
    public_urls: list = [
        path(f'{api_version}/', include(public_urls))
    ]

urlpatterns = public_urls

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
