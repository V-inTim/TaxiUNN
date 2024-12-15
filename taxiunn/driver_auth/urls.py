from django.urls import path

from .views import (
    RegistrationView,
    VerificationOfRegistrationView,
    LoginView,
    RefreshView,
    DriverPasswordRecoveryView,
    DriverPasswordRecoveryVerifyView,
    DriverPasswordRecoveryChangeView,
)

urlpatterns = [
    path(
        'register',
        RegistrationView.as_view(),
        name='registration',
    ),
    path(
        'activate',
        VerificationOfRegistrationView.as_view(),
        name='verify_register',
    ),
    path(
        'login',
        LoginView.as_view(),
        name='login_driver',
    ),
    path(
        'refresh',
        RefreshView.as_view(),
        name='refresh_driver',
    ),
    path(
        'password-recovery',
        DriverPasswordRecoveryView.as_view(),
        name='recovery_driver',
    ),
    path(
        'password-recovery/verify',
        DriverPasswordRecoveryVerifyView.as_view(),
        name='recovery_verify_driver',
    ),
    path(
        'password-recovery/change',
        DriverPasswordRecoveryChangeView.as_view(),
        name='recovery_change_driver',
    ),
]
