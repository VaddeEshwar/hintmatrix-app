from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from utils.generate_key import id_generator


class LoginSessionSerializers(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    request_id = serializers.UUIDField(write_only=True)
    access = serializers.EmailField(write_only=True)


class ForgotPasswordOTPSerializers(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    request_id = serializers.UUIDField(write_only=True)
    email = serializers.EmailField(write_only=True)

    def validate(self, attrs):

        # send OTP to email
        _request = self.context.get("request")
        _email = attrs.get("email")
        _request.session["email"] = _email

        try:
            User.objects.get(username=_email)
        except Exception:
            raise serializers.ValidationError("Invalid details", "FOTP02")
        _otp = id_generator(size=6)
        print(_otp, _request.session.get("otp"))
        _request.session["otp"] = _otp
        attrs["otp"] = _otp
        # try:
        #     _subject = "Final Account OTP"
        #     _body = f"""Reset password OTP: {_otp}"""
        #     # ToDO: django sent_email error: invalid '@'.
        #     _do_email = send_mail(
        #         _subject,
        #         _body,
        #         settings.DEFAULT_FROM_EMAIL,
        #         list(_email),
        #         fail_silently=False,
        #     )
        #     print(_do_email)
        #     _do_email = EmailMessage(
        #     _subject, _body, to=tuple(_email))
        #     _do_email.send()
        # except Exception as e:
        #     raise serializers.ValidationError(detail=str(e), code="FOTP01")

        return attrs


class ForgotPasswordOTPVerifySerializers(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    request_id = serializers.UUIDField(write_only=True)
    email = serializers.EmailField(write_only=True)
    otp = serializers.CharField(write_only=True, min_length=6, max_length=6)

    def validate(self, attrs):
        # Validate OTP.
        _request = self.context.get("request")
        _email = attrs.get("email")
        _otp = attrs.get("otp")
        _session_email = _request.session("email")
        if not _email == _session_email:
            raise serializers.ValidationError("something went wrong.", "FOTP03")

        try:
            User.objects.get(username=_email)
        except Exception:
            raise serializers.ValidationError("Invalid details", "FOTP02")

        _session_otp = _request.session.get("otp")

        if not _otp == _session_otp:
            raise serializers.ValidationError(detail="invalid OTP", code="FOTP03")

        _request.session["is_otp_verify"] = True

        return attrs


class ResetPasswordSerializers(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    request_id = serializers.UUIDField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password1 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # reset password.
        _request = self.context.get("request")
        _is_opt_verify = _request.session.get("is_otp_verify")
        if not _is_opt_verify:
            raise serializers.ValidationError(detail="in valid request", code="RSP04")

        _email = attrs.get("email")
        _session_email = _request.session.get("email")
        if not _email == _session_email:
            raise serializers.ValidationError("something went wrong.", "RSP05")

        _psw = attrs.get("password")
        _psw1 = attrs.get("password1")
        if not _psw == _psw1:
            raise serializers.ValidationError("in valid password", "RSP05")

        try:
            validate_password(_psw)
        except Exception as e:
            raise serializers.ValidationError(str(e), "RSP07")

        try:
            _user = User.objects.get(username=_email)
            _user.set_password(_psw)
            _user.save()
            attrs["is_reset"] = True

        except Exception:
            raise serializers.ValidationError("Invalid details", "RSP06")

        return attrs


class SignUpSerializers(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    request_id = serializers.UUIDField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password1 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # sign up.
        # _request = self.context.get("request")
        _email = attrs.get("email")
        _psw = attrs.get("password")
        _psw1 = attrs.get("password1")
        if not _psw == _psw1:
            raise serializers.ValidationError("in valid password", "RSP05")

        try:
            _user = User.objects.filter(username=_email)
            if not _user.exists():
                _user = User(username=_email, email=_email)
                _user.set_password(_psw)
                _user.save()
            else:
                raise serializers.ValidationError("user exists")
        except Exception:
            raise serializers.ValidationError("user exists.", "SUP06")

            # ToDo: send verify OTP to email.

        return attrs
