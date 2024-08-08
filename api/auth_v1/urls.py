from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from api.auth_v1.views import (
    ForgotPasswordOTPAPI,
    ForgotPasswordOTPVerifyAPI,
    ResetPasswordAPI,
    SignUpAPI,
    LoginSessionAPI,
)

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/
# index.html
urlpatterns = [
    # session login
    path("login/session/", LoginSessionAPI.as_view(), name="session-login"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("forgot-password/", ForgotPasswordOTPAPI.as_view(), name="forgot-password"),
    path(
        "forgot-password/otp/",
        ForgotPasswordOTPVerifyAPI.as_view(),
        name="forgot-password-otp",
    ),
    path("reset-password/", ResetPasswordAPI.as_view(), name="reset-password"),
    path("signup/", SignUpAPI.as_view(), name="sign-up"),
]
