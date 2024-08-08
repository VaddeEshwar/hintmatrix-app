from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from website.views import (
    QuestionView,
    SignUpView,
    ArticleShipView,
    BlogView,
    ResetPasswordRequestView,
    SignUpDoneView,
)

app_name = "website"
urlpatterns = [
    # non session URL's
    path("question/", QuestionView.as_view(), name="n-question"),
    path("question/<str:q_slug>/", QuestionView.as_view(), name="n-question_details"),
    path("blog/", BlogView.as_view(), name="blog"),
    path("articleship/", ArticleShipView.as_view(), name="articleship"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signup/done/", SignUpDoneView.as_view(), name="signup-done"),
    path(
        "forgot-password/", ResetPasswordRequestView.as_view(), name="forgot-password"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
