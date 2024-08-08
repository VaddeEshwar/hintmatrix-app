from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.v1.serializers import (
    QuestionAttributeSerializer,
    QuestionAddSerializer,
    QuestionReadSerializer,
    QuestionsSerializer,
)
from config.models import TableAttribute
from question.models import Exam
from utils.api_utils import render_api_response


class QuestionsView(ListAPIView):
    success, code, msg = False, "QUN01", ""
    rtn, http_code = [], 200

    serializer_class = QuestionsSerializer

    def get_queryset(self):
        return Exam.get_queryset(is_active=True)

    def get(self, *args, **kwargs):
        _data = self.serializer_class(self.get_queryset()[:10], many=True)
        self.rtn = list(_data.data)
        self.success = True

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )


class QuestionReadView(RetrieveAPIView):
    success, code, msg = False, "QRED01", ""
    rtn, http_code = [], 200

    serializer_class = QuestionReadSerializer

    def get(self, *args, **kwargs):
        _slug = kwargs.get("slug")
        _data = self.serializer_class(data={"slug": _slug})
        if _data.is_valid():
            _valid = _data.validated_data
            self.rtn = [
                {
                    "title": _valid.get("title"),
                    "slug": _valid.get("slug").__str__(),
                    "details": _valid.get("details"),
                }
            ]
            self.success = True
        else:
            self.msg, self.code, self.http_code = (_data.errors, "QRED02", 400)

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )


class QuestionAddAPI(CreateAPIView):
    success, code, msg = False, "QADD01", ""
    rtn, http_code = [], 200

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = QuestionAddSerializer

    def post(self, *args, **kwargs):
        _data = self.serializer_class(data=self.request.data)
        if _data.is_valid():
            _valid = _data.validated_data
            self.rtn = [
                {"slug": _valid.get("slug").__str__(), "title": _valid.get("title")}
            ]
            self.success = True
        else:
            self.msg, self.code, self.http_code = (_data.errors, "QADD02", 400)

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )


class QuestionAttributeAPI(ListAPIView):
    success, code, msg = False, "QLST01", ""
    rtn, http_code = [], 200

    # SessionAuthentication, BasicAuthentication,
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = QuestionAttributeSerializer

    def get_queryset(self):
        return TableAttribute.get_queryset(is_active=True)

    def get(self, *args, **kwargs):
        _data = self.serializer_class(self.get_queryset(), many=True)
        self.rtn = list(_data.data)
        self.success, self.code = (True, "QLST02")

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )
