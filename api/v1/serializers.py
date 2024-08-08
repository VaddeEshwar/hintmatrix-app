from rest_framework import serializers

from config.models import TableAttribute, TableHeader
from question.models import Exam, ExamQuestion


class QuestionsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ("slug", "title")

    @staticmethod
    def get_title(obj):
        if not obj.name:
            return obj.slug.__str__()
        return obj.name


class QuestionReadSerializer(serializers.Serializer):
    slug = serializers.UUIDField()

    def validate(self, attrs):
        _slug = attrs.get("slug").__str__()

        _qun_details = ExamQuestion.get_queryset(exam__slug=_slug).select_related(
            "exam", "tbl_header", "attribute"
        )

        _name = None
        _details = []
        for _detail in _qun_details:
            _details.append(
                {
                    "particular": _detail.tbl_header.name,
                    "attr_code": _detail.attribute.code,
                    "attr": _detail.attribute.name,
                    "amount": _detail.amount,
                }
            )

            if not _name:
                _name = _detail.exam.name
                if not _name:
                    _name = _slug

        attrs["title"] = _name
        attrs["slug"] = _slug
        attrs["details"] = _details

        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


def save_particulars(exam, particulars, attr_code, attr_query_set, list_amount):
    _header, is_created = TableHeader.get_queryset().get_or_create(name=particulars)
    _attr = attr_code_id_dict(attr_query_set)
    for index, debit in enumerate(attr_code):
        debt_obj = {
            "exam": exam,
            "tbl_header": _header,
            "attribute_id": _attr.get(debit),
            "amount": list_amount[index],
        }
        d1 = ExamQuestion(**debt_obj)
        d1.save()

    return True


def attr_code_id_dict(query_set):
    _d = dict()
    for _itm in query_set:
        _d[_itm.get("code")] = _itm.get("id")
    return _d


class QuestionAddSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    dr_attr_code = serializers.ListField()
    dr_amount = serializers.ListField()
    cr_attr_code = serializers.ListField()
    cr_amount = serializers.ListField()
    adj_attr_code = serializers.ListField(required=False)
    adj_amount = serializers.ListField(required=False)

    def validate(self, attrs):
        _name = attrs.get("title")
        _code_dr = attrs.get("dr_attr_code")
        _code_dr_ins = TableAttribute.get_queryset(code__in=_code_dr).values(
            "code", "id"
        )
        _amount_dr = attrs.get("dr_amount")
        if not _code_dr_ins.count() == len(_amount_dr):
            raise serializers.ValidationError(
                detail="miss match of debit particular and amount", code="ADD01"
            )

        _code_cr = attrs.get("cr_attr_code")
        _code_cr_ins = TableAttribute.get_queryset(code__in=_code_cr).values(
            "code", "id"
        )
        _amount_cr = attrs.get("cr_amount")
        if not _code_cr_ins.count() == len(_amount_cr):
            raise serializers.ValidationError(
                detail="miss match of credit particular and amount", code="ADD02"
            )

        _code_adj = attrs.get("adj_attr_code")
        _amount_adj = attrs.get("adj_amount")
        _code_adj_ins = None
        if _code_adj and _amount_adj:
            _code_adj_ins = TableAttribute.get_queryset(code__in=_code_adj).values(
                "code", "id"
            )
            if len(_amount_adj) > 0 and (not _code_adj_ins.count() == len(_amount_adj)):
                raise serializers.ValidationError(
                    detail="miss match of adjustments and amount", code="ADD03"
                )

        exam_obj = {"name": _name, "is_active": True}
        ex = Exam(**exam_obj)
        ex.save()

        save_particulars(ex, "debit particulars", _code_dr, _code_dr_ins, _amount_dr)

        save_particulars(ex, "credit particulars", _code_cr, _code_cr_ins, _amount_cr)

        if _code_adj and _amount_adj:
            save_particulars(ex, "adjustments", _code_adj, _code_adj_ins, _amount_adj)

        attrs["slug"] = ex.slug.__str__()
        attrs["title"] = ex.name

        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class QuestionAttributeSerializer(serializers.ModelSerializer):
    s_name = serializers.SerializerMethodField()

    class Meta:
        model = TableAttribute
        fields = ("code", "name", "s_name")

    @staticmethod
    def get_s_name(obj):
        return obj.short_name
