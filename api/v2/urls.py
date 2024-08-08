from django.urls import path

from api.v2.views import RequestAPIView

urlpatterns = [
    path("<str:module>/<uuid:slug>/", RequestAPIView.as_view(), name="get-attributes"),
]
