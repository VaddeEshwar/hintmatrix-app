from django.urls import path
from django.views.generic import TemplateView

app_name = "website_v1"
urlpatterns = [
    # session
    path(
        "my-app/question/add/",
        TemplateView.as_view(template_name="v1/secure/add-question.html"),
        name="dashboard",
    ),
    path(
        "my-app/",
        TemplateView.as_view(template_name="v1/secure/dashboard.html"),
        name="dashboard",
    ),
    # non session
    path("login/", TemplateView.as_view(template_name="v1/login.html"), name="login"),
    path("", TemplateView.as_view(template_name="v1/index.html"), name="index"),
]
