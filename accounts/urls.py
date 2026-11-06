from .views import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PendingUsersView,
    RegisterView,
    VerifyUserView,
)
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path

urlpatterns = [

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
     path('users/pending/', PendingUsersView.as_view(), name='pending-users'),
    path('users/<int:pk>/verify/', VerifyUserView.as_view(), name='verify-user'),
    path('me/', MeView.as_view(), name='me'),
]

