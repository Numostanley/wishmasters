from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserOnboarding)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login', views.UserLoginView.as_view()),
    path('auth/change_password', views.PasswordChangeAPIView.as_view()),
    path("details", views.UserDetailsAPIView.as_view()),

]
