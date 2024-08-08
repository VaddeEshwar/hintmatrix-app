from django.contrib.auth import login
from rest_framework.generics import CreateAPIView

from api.auth_v1.serializers import (
    ForgotPasswordOTPSerializers,
    ForgotPasswordOTPVerifySerializers,
    ResetPasswordSerializers,
    SignUpSerializers,
)
from utils.api_utils import render_api_response


class LoginSessionAPI(CreateAPIView):
    success, code, msg = False, "LS00", ""
    data, http_code = [], 404

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            login(self.request, self.request.user)
            self.success, self.code, self.http_code = True, "LS01", 200
        else:
            self.msg = "invalid"
            self.success, self.code, self.http_code = False, "LS02", 406

        return render_api_response(
            self.data,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )


class ForgotPasswordOTPAPI(CreateAPIView):
    success, code, msg = False, "FP00", ""
    rtn, http_code = [], 404

    serializer_class = ForgotPasswordOTPSerializers

    def post(self, *args, **kwargs):
        _data = self.serializer_class(
            data=self.request.data, context={"request": self.request}
        )
        if not _data.is_valid():
            self.msg, self.http_code, self.code = (_data.errors, 406, "FP01")
        else:
            _v_data = _data.validated_data
            self.rtn = [{"otp": _v_data.get("otp")}]
            self.success, self.code, self.http_code = True, "FP02", 200

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )


class ForgotPasswordOTPVerifyAPI(CreateAPIView):
    success, code, msg = False, "FPOV00", ""
    rtn, http_code = [], 404

    serializer_class = ForgotPasswordOTPVerifySerializers

    def post(self, *args, **kwargs):
        _data = self.serializer_class(
            data=self.request.data, context={"request": self.request}
        )

        if not _data.is_valid():
            self.msg, self.http_code, self.code = (_data.errors, 406, "FPOV01")
        else:
            self.success, self.code, self.http_code = (True, "FPOV02", 200)

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )


class ResetPasswordAPI(CreateAPIView):
    success, code, msg = False, "RSP00", ""
    rtn, http_code = [], 404

    serializer_class = ResetPasswordSerializers

    def post(self, *args, **kwargs):
        _data = self.serializer_class(
            data=self.request.data, context={"request": self.request}
        )

        if not _data.is_valid():
            self.msg, self.http_code, self.code = (_data.errors, 406, "FPOV01")
        else:
            self.success, self.code, self.msg = (
                True,
                "FPOV02",
                "password reset successfully",
            )

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )


class SignUpAPI(CreateAPIView):
    success, code, msg = False, "SUP00", ""
    rtn, http_code = [], 404

    serializer_class = SignUpSerializers

    def post(self, *args, **kwargs):
        _data = self.serializer_class(
            data=self.request.data, context={"request": self.request}
        )

        if not _data.is_valid():
            self.msg, self.http_code, self.code = (_data.errors, 406, "SUP01")
        else:
            self.success, self.code, self.msg, self.http_code = (
                True,
                "SUP02",
                "user signup successfully",
                200,
            )

        return render_api_response(
            self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
        )
