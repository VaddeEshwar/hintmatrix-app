from uuid import uuid4

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from config.models import (
    TableHeader, TableAttribute, Chapter, QuestionCategory
)


class Exam(models.Model):
    slug = models.SlugField(
        default=uuid4, unique=True, help_text=_("row id"), editable=False
    )
    question_code = models.CharField(
        max_length=16, null=True, blank=True,
        help_text="Question order by serial code"
    )
    name = models.CharField(max_length=5120, blank=True, null=True)
    # none=> draft | False => disable | True => active
    is_active = models.BooleanField(null=True, default=False, db_index=True)
    question_category = models.ForeignKey(
        QuestionCategory, on_delete=models.SET_NULL, null=True, default=None
    )
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True)

    c_on = models.DateTimeField(auto_now_add=True)
    u_on = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ("question_code",)

    def __str__(self):
        return f"""{self.slug} - {self.name}"""

    @classmethod
    def get_queryset(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    @classmethod
    def get_slug_by_exam(cls, slug):
        return cls.get_queryset(slug=slug).first()

    @classmethod
    def get_recent_exam(cls, limit=5):
        return cls.get_queryset(is_active=True)[:limit]

    @staticmethod
    def get_exam_detail(question_slug: uuid4, table_header: str):
        return ExamQuestion.get_queryset(
            exam__slug=question_slug, tbl_header__name=table_header
        ).order_by("c_on")

    @cached_property
    def get_ch4_transaction(self):
        return ExamQuestion.get_queryset(
            exam=self, tbl_header__name="transaction"
        ).order_by("c_on")

    @cached_property
    def get_ch3_transaction(self):
        return ExamQuestion.get_queryset(
            exam=self, tbl_header__name="transaction"
        ).order_by("c_on")

    @cached_property
    def get_debit_balance(self):
        return ExamQuestion.get_queryset(
            exam=self, tbl_header__name="debit particulars"
        ).order_by("c_on")

    @cached_property
    def get_credit_balance(self):
        return ExamQuestion.get_queryset(
            exam=self, tbl_header__name="credit particulars"
        ).order_by("c_on")

    @cached_property
    def get_adjustment(self):
        return ExamQuestion.get_queryset(
            exam=self, tbl_header__name="adjustments")

    @cached_property
    def get_name_in_url(self):
        if not self.name:
            return self.slug.__str__()
        name = self.name.split()
        return "-".join(name)

    @cached_property
    def get_ui_name(self):
        if not self.name:
            return self.slug.__str__()
        return self.name


class ExamQuestion(models.Model):
    slug = models.SlugField(
        default=uuid4, unique=True, help_text=_("row id"), editable=False
    )
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    tbl_header = models.ForeignKey(
        TableHeader, null=True, on_delete=models.SET_NULL)
    tr_date = models.DateField(null=True,)
    attribute = models.ForeignKey(
        TableAttribute, null=True, on_delete=models.SET_NULL)
    # ch1 (without adjustment) and ch2 (with adjustment)
    amount = models.FloatField(default=0)

    # for ch3 (journal chapter) required amount2
    amount2 = models.FloatField(default=0)
    ext_jf_lf = models.CharField(max_length=32, null=True)
    is_active = models.BooleanField(null=True, default=False, db_index=True)
    note = models.CharField(max_length=64, null=True)

    c_on = models.DateTimeField(auto_now_add=True)
    u_on = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ("-u_on",)

    def __str__(self):
        return f"""{self.exam} - {self.tbl_header} -
                    {self.attribute} - {self.amount}"""

    @classmethod
    def get_queryset(cls, **kwargs):
        return cls.objects.filter(**kwargs)
