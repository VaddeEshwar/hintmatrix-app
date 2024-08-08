from copy import deepcopy

schema = {"name": {"type": "string"}}
base_schema = dict(
    requestId=dict(type="string", required=True),
    accessToken=dict(type="string"),
    request=dict(
        type="dict",
        required=True,
        schema=dict(
            operationName=dict(
                type="string",
                required=True,
                allowed=[
                    "fetch",
                    "save",
                ],
            ),
            variables=dict(
                type="dict",
                required=True,
                # schema define separately, based on operation name.
                schema=dict(
                    modelName=dict(type="string", required=True, minlength=3),
                    pageSize=dict(type="integer"),
                ),
            ),
        ),
    ),
)

base_fetch_schema = dict(
    schema=dict(
        fields=dict(
            type="list",
            required=True,
            schema=dict(type="string", minlength=2),
        ),
        filters=dict(
            type="list",
            schema=dict(
                type="dict",
                schema=dict(
                    field=dict(type="string", required=True, minlength=2),
                    value=dict(type="string|list|boolean", required=True),
                    operator=dict(type="string", required=True, minlength=2),
                ),
            ),
        ),
        orderBy=dict(type="list", schema=dict(type="string", minlength=2)),
    )
)

fetch_schema = deepcopy(base_schema)
fetch_schema["request"]["schema"]["variables"]["schema"].update(
    **base_fetch_schema["schema"]
)
# pprint(fetch_schema)

# fetch_data_model = dict(
#     operationName="fetch",
#     variables=dict(modelName="", fields=[], filter=[], orderBy=[]),
# )
#
# # {"role": {"type": "string", "allowed": ["agent", "client", "supplier"]}}
# fetch = dict(
#     operationName={"type": "string", "allowed": ["fetch", "save", "login"]},
#     variables={
#         "type": "dict",
#         "schema": {
#             "modelName": {"type": "string"},
#             "field": {"type": "list"},
#             "filter": {
#                 "type": "list",
#                 "items": [
#                     {
#                         "field": {"type": "string"},
#                         "operator": {"type": "string"},
#                         "value": {"type": "string"},
#                     }
#                 ],
#             },
#             "orderBy": {"type": "list"},
#         },
#     },
# )
#
# fetch1 = {
#     "operationName": "fetch",
#     "variables": {
#         "modelName": "Exam",
#         "fields": ["name", "c_on", "slug", "is_active"],
#         "filters": [
#             {"field": "is_active", "value": True, "operator": "eq"},
#             {
#                 "field": "slug",
#                 "value": "1aa94a98-a998-48b2-a004-b6ca1e94e6ad",
#                 "operator": "eq",
#             },
#         ],
#         "orderBy": ["name"],
#         "pageSize": 10,
#     },
# }
