from django.urls import path

from api.v1.views import (
    QuestionAttributeAPI,
    QuestionAddAPI,
    QuestionReadView,
    QuestionsView,
)

urlpatterns = [
    # get attribute of table
    path("question/attributes/", QuestionAttributeAPI.as_view(), name="get-attributes"),
    # create question
    path("question/add/", QuestionAddAPI.as_view(), name="add-question"),
    # view question detail
    path(
        "question/<uuid:slug>/<str:title>/",
        QuestionReadView.as_view(),
        name="add-question",
    ),
    # view questions
    path("question/", QuestionsView.as_view(), name="questions"),
]
