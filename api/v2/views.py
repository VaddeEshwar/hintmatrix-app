from rest_framework import generics

from api.v2.proces_request import ProcessRequest
from api.v2.serializers import RequestSerializer
from utils.api_utils import render_api_response_v2


class RequestAPIView(generics.GenericAPIView):
    success, code, msg = False, "RAV01", ""
    rtn, data_support, http_code = [], {}, 200

    serializer_class = RequestSerializer

    def get(self, *args, **kwargs):
        module = self.kwargs.get("module")
        data = self.request.data
        _data = self.serializer_class(data=data)
        if _data.is_valid():
            try:
                pr = ProcessRequest(data)
                self.rtn, self.data_support = pr.run()
                self.success = True
            except Exception as e:
                self.code = "RAV03"
                self.msg = e.__str__()
        else:
            self.code = "RAV02"
            self.msg = _data.errors

        self.data_support["module"] = module

        return render_api_response_v2(
            request_id=self.request.data.get("requestId"),
            data=self.rtn,
            SUCCESS=self.success,
            code=self.code,
            msg=self.msg,
            http_code=self.http_code,
            data_support=self.data_support,
        )

    def post(self, *args, **kwargs):
        return self.get(*args, *kwargs)

    def put(self, *args, **kwargs):
        return self.get(*args, *kwargs)
