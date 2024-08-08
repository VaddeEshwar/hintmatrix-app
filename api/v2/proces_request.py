import json
from django.apps import apps
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

operator = {
    "eq": "=",
    "lt": "__lt",
    "lte": "__lte",
    "gt": "__gt",
    "gte": "__gte",
    "in": "__in",
}

fetch_model_permission = dict(Chapter=True, QuestionCategory=True, Exam=True)

save_model_permission = dict()


def get_all_models() -> dict:
    models = dict()
    for mdl in apps.get_models():
        models[mdl.__name__] = mdl
    return models


def get_model_local_fields(model) -> dict:
    fields = dict()
    for fld in model._meta.local_fields:
        fields[fld.name] = fld
    return fields


def get_model_fields(model) -> dict:
    fields = dict()
    for fld in model._meta.fields:
        fields[fld.name] = fld
    return fields


def validate_all_fields_exist(field1: list, field2: list) -> bool:
    return all(fld in field2 for fld in field1)


class ProcessRequest(object):
    def __init__(self, payload):
        self.payload = payload
        self.payload_request = self.payload.get("request")
        self.operation_name = self.payload_request.get("operationName")
        self.variables = self.payload_request.get("variables")
        self.model_name = self.variables.get("modelName")
        self.model_class = None
        self.fields = self.variables.get("fields", "")
        self.model_class_fields = None
        self.filters = self.variables.get("filters", [])
        self.order_by = self.variables.get("orderBy", [])
        self.page_size = self.variables.get("pageSize", 30)

    def validate_payload(self):
        """
        to validate schema
        based on Operation, payload must validate through Cerberus pre-defined
        schema.
        if not valid, return invalid data.
        if yes, send process request.
        :return:
        """
        print(self)
        return True

    def get_model(self):
        return get_all_models().get(self.model_name)

    def make_filter(self) -> dict:
        filter_fields = {}
        if not self.model_class_fields:
            self.model_class = self.get_model()
            self.model_class_fields = get_model_local_fields(
                model=self.model_class)

        # filter validate
        for flt in self.filters:
            _fld = self.model_class_fields.get(flt.get("field"))
            if not _fld:
                raise
            _opt = operator.get(flt.get("operator"))
            if not _opt:
                raise

            filter_fields[f"{_fld.name}{_opt.replace('=', '')}"] = flt.get(
                "value")

        return filter_fields

    def make_order_by(self):
        order_by_fields = []

        if not self.model_class_fields:
            self.model_class = self.get_model()
            self.model_class_fields = get_model_local_fields(
                model=self.model_class)

        # order by validate
        for o_field in self.order_by:
            of = o_field
            if o_field.startswith("-"):
                of = of[1:]
            if not self.model_class_fields.get(of):
                raise
            order_by_fields.append(o_field)
        return order_by_fields

    @staticmethod
    def make_query_set_to_json(query_set):
        data = json.dumps(list(query_set), cls=DjangoJSONEncoder)
        return json.loads(data)

    def save(self):
        """
        model_payload = {
            "requestId": "uuid4",
            "accessToken": "",
            "request": {
                "operationName": "save",
                "variables": {
                    "modelName": "Question",
                    # for update
                    "slug": "uuid4",
                    "filters": [
                        {"field": "field1", "value": ["abc"], "operator": "eq"}
                    ],
                    # to save
                    "saveInput": {"field1": "value", "field2": "value"},
                },
            },
        }
        :return:
        """

        data, total = [], 0
        self.model_class = self.get_model()

        if not save_model_permission.get(self.model_name):
            raise Exception("invalid query")

        self.model_class_fields = get_model_local_fields(
            model=self.model_class)
        save_input = self.variables.get("saveInput")

        update_slug = self.variables.get("slug")
        if not update_slug:
            # create new record
            record = self.model_class(**save_input)
            record.save()
            data = model_to_dict(record, exclude=["id", "is_active", "u_on"])
            data.update(slug=record.slug.__str__())
            total = 1
        else:
            # update record
            filter_fields = self.make_filter()
            filter_fields["slug"] = self.variables.get("slug")
            q_set = self.model_class.get_queryset(**filter_fields)
            total = q_set.count()
            if total > 0:
                update = q_set.update(**save_input)
                if not update:
                    raise
                data = {"slug": self.variables.get("slug")}

        return data, total

    def fetch(self) -> ([dict], int):
        """
        model_payload = {
            "requestId": "uuid4",
            "accessToken": "",
            "request": {
                "operationName": "fetch",
                "variables": {
                    "modelName": "Question",
                    "fields": ["field1", "field2", "field3"],
                    "filters": [
                        {"field": "field1", "value": ["abc"], "operator": "eq"}
                    ],
                    "orderBy": ["field2", "-field4"],
                },
            },
        }
        :return: [{}], 0
        """
        self.model_class = self.get_model()
        if not fetch_model_permission.get(self.model_name):
            raise Exception("invalid query")

        self.model_class_fields = get_model_local_fields(
            model=self.model_class)

        is_valid_all_fields = validate_all_fields_exist(
            self.fields, list(self.model_class_fields.keys())
        )
        if not is_valid_all_fields:
            raise

        # filter validate
        filter_fields = self.make_filter()

        # order by validate
        order_by_fields = self.make_order_by()

        # total records
        query_set = self.model_class.get_queryset(**filter_fields).order_by(
            *order_by_fields
        )
        total = query_set.count()
        data = []
        if total > 0:
            data = query_set.values(*self.fields)[0: self.page_size]
            data = self.make_query_set_to_json(data)

        return data, total

    def run(self) -> (list, dict):
        operations = dict(fetch=self.fetch, save=self.save)
        do_operation = operations.get(self.operation_name)
        data, total = do_operation()
        data_support = {"total": total}
        return data, data_support
