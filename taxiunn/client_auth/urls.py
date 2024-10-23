from django.urls import path

from .views import RegisterView, ActivateView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('activate', ActivateView.as_view(), name='activate'),
]
