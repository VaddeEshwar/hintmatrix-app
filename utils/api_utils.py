from django.http import JsonResponse


def render_api_response(data, **kwargs):
    """
    # TODO: Update based on response type demand
    # content = JSONRenderer().render(serializer.data)
    response format
    {"status": success/failure, data: [], error_message: "", code:""}
    :param data:
    :param kwargs:
    :return:
    """
    res_obj = dict(
        status="FAILURE", code=kwargs.pop("code", "na"), message=kwargs.pop("msg", "")
    )
    status = kwargs.pop("SUCCESS", True)
    if status:
        res_obj["status"] = "SUCCESS"
    res_obj["data"] = [data] if not type(data) == list else data

    _http = dict(status=kwargs.pop("http_code", 200))
    res_obj.update(kwargs)

    return JsonResponse(res_obj, **_http)


def render_api_response_v2(request_id, data, **kwargs):
    """
    # TODO: Update based on response type demand
    # content = JSONRenderer().render(serializer.data)
    response format
    {requestId: "", "status": success/failure, response:{data: [], kwargs: {}}, message: "", code: ""}
    :param request_id:
    :param data:
    :param kwargs:
    :return:
    """
    res_obj = dict(
        requestId=request_id,
        status="FAILURE",
        response=dict(
            data=[data] if not type(data) == list else data,
            dataSupport=dict(),
        ),
        code=kwargs.pop("code", "-"),
        message=kwargs.pop("msg", "-"),
    )

    status = kwargs.pop("SUCCESS", True)
    if status:
        res_obj["status"] = "SUCCESS"

    _http = dict(status=kwargs.pop("http_code", 200))
    res_obj["response"]["dataSupport"].update(kwargs.get("data_support"))

    return JsonResponse(res_obj, safe=False, **_http)
