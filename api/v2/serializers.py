from rest_framework import serializers
from api.v2.request_schema import fetch_schema
from cerberus import Validator


def validate_request_body(request):
    """
    based on operation name, schema should fetch from schema folder and validate the same.
    https://docs.python-cerberus.org/en/latest/index.html
    """
    v = Validator()
    v1 = v.validate(request, fetch_schema)
    if not v1:
        print(v1.errors)

    return True


class RequestSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        return validated_data

    def create(self, validated_data):
        return validated_data

    requestId = serializers.UUIDField(format="hex_verbose")
    request = serializers.JSONField()
    accessToken = serializers.CharField()

    def validate(self, attrs):
        v = Validator()
        try:
            v1 = v.validate(dict(attrs).copy(), fetch_schema)
            if not v1:
                print(v1.errors)
        except Exception as e:
            print(e.__str__())

        return attrs
