from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

from config.lookups import ARITHMETIC, ARITHMETIC_DICT
from config.models import RuleEngine, TableAttribute, TableHeader, TableName
from question.models import Exam, ExamQuestion
from utils.cache_control import get_cache_code_by_name
from utils.models import AbstractModel


class ExamAnswer(AbstractModel):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    qun = models.ForeignKey(ExamQuestion, null=True, on_delete=models.SET_NULL)

    tbl_name = models.ForeignKey(
        TableName, null=True, on_delete=models.SET_NULL
    )
    tbl_header = models.ForeignKey(
        TableHeader, null=True, on_delete=models.SET_NULL
    )
    attribute = models.ForeignKey(
        TableAttribute, null=True, on_delete=models.SET_NULL
    )

    # 2 => addition, 3=> subtraction, 0 => no operation.
    operation = models.PositiveSmallIntegerField(
        null=True, default=0, verbose_name="arithmetic", choices=ARITHMETIC
    )
    rule = models.ForeignKey(RuleEngine, null=True, on_delete=models.SET_NULL)
    amount = models.FloatField(default=0)
    note = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ("-u_on",)
        unique_together = (
            "user",
            "qun",
            "tbl_name",
            "tbl_header",
            "attribute",
        )

    def __str__(self):
        return (
            f"{self.exam} - {self.tbl_header} - "
            f"{self.attribute} - {self.amount}"
        )

    @classmethod
    def answer_save(
        cls,
        user,
        qun,
        rule,
        tbl_name,
        tbl_header,
        attribute,
        amount,
        operation,
        note=None,
    ):
        data_dict = dict()
        data_dict["user"] = user
        data_dict["exam"] = qun.exam
        data_dict["qun"] = qun
        data_dict["tbl_name"] = tbl_name
        data_dict["tbl_header"] = tbl_header
        data_dict["attribute"] = attribute
        data_dict["operation"] = operation
        data_dict["rule"] = rule
        data_dict["amount"] = amount
        data_dict["note"] = note

        rec = cls(**data_dict).save()

        return rec

    @classmethod
    def get_most_answered_exam(cls, limit=5):
        return cls.get_queryset(exam__is_active=True).values(
            "exam__id", "exam__slug", "exam__name"
        )[:limit]

    @classmethod
    def get_last_answered_exam(cls, user, limit=5):
        return cls.get_queryset(user=user, exam__is_active=True).values(
            "exam__id", "exam__slug", "exam__name"
        )[:limit]

    @property
    def operation_name(self):
        return ARITHMETIC_DICT.get(self.operation)


class AnswerEvent(AbstractModel):
    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True)
    qun = models.ForeignKey(ExamQuestion, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, default=None, null=True
    )
    description = models.CharField(max_length=512)
    valid = models.BooleanField(default=False, null=True)
    action = models.CharField(max_length=512, null=True)
    # user choice
    user_answer = models.CharField(max_length=512, null=True)
    # user / system
    answer_by = models.CharField(max_length=512, null=True)
    # hint information of the event
    hint = models.CharField(max_length=512, null=True)
    # random tag for old data
    archive = models.CharField(max_length=8, null=True, editable=False)
    # score of the event
    score = models.FloatField(default=0, editable=False, db_index=True)

    def __str__(self):
        return f"{self.exam}-{self.description}-{self.valid}"

    @classmethod
    def add_event(
        cls,
        table,
        particular,
        add_sub,
        exam_question,
        user,
        valid,
        action,
        answer_by="user",
        hint="n/a",
    ):
        # action by
        if action and action.startswith("auto"):
            answer_by = "system"

        # tbl, particular, add_sub, qun_attr, request.user, True
        _tbl_name = get_cache_code_by_name(TableName, table)
        if action == "step1":
            _particular = get_cache_code_by_name(TableAttribute, particular)
        else:
            _particular = get_cache_code_by_name(TableHeader, particular)

        if add_sub == "sub":
            add_sub = "subtract"

        _user_answer = "attempted"
        if add_sub:
            _user_answer += f" to {add_sub}"

        _user_answer += f""" on {_particular} of {_tbl_name}"""
        description = (
            f"from {exam_question.tbl_header.name} of "
            f"{exam_question.attribute.name} amount is "
            f"{exam_question.amount} >> {_user_answer}."
        )
        _score = 0.0
        if answer_by == "user":
            _eve_exists = cls.get_queryset(
                user=user, qun=exam_question, archive=None
            ).exclude(valid=True)
            if not _eve_exists.exists():
                _score = 1.0
            elif _eve_exists.count() < 2:
                _score = 0.5

        _c = cls(
            exam=exam_question.exam,
            qun=exam_question,
            user=user,
            valid=valid,
            description=description,
            action=action,
            user_answer=_user_answer,
            answer_by=answer_by,
            hint=hint,
            score=_score,
        )
        _c.save()
        return _c

    @classmethod
    def total_marks(cls, user):
        """
        It returns the sum of the scores of all the answers submitted by
        the user
        :return: The total marks of the user.
        """
        score = (
            cls.get_queryset(user=user, score__gt=0)
            .values("score")
            .annotate(total_marks=Sum("score"))
            .order_by("-total_marks")
            .values_list("total_marks", flat=True)
        )
        return sum(score)

    @classmethod
    def chapter_wise_marks(cls, user, chapter=None):
        score = cls.get_queryset(user=user, score__gt=0)
        if chapter:
            score = score.filter(exam__chapter=chapter)

        score = (
            score.values("exam__chapter__name")
            .annotate(total_marks=Sum("score"))
            .order_by("-total_marks")
            .values_list("exam__chapter__name", "total_marks")
        )

        return score
