from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, IntegrityError

from config.lookups import (
    ARITHMETIC,
    RELATIONSHIP,
    ARITHMETIC_BY_VALUE,
    ARITHMETIC_DICT,
    RELATIONSHIP_DICT,
)
from utils.generate_key import code_generator
from utils.models import AbstractModel


class Course(AbstractModel):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.code}:{self.name}"


class Chapter(AbstractModel):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=8, default=None)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.code}:{self.name}"


class QuestionCategory(AbstractModel):
    code = models.CharField(max_length=8, default=None)
    name = models.CharField(max_length=64)
    order_of = models.PositiveSmallIntegerField(
        default=0, help_text="order of Question Category"
    )

    class Meta:
        ordering = ("order_of",)

    def __str__(self):
        return f"{self.code}:{self.name}"

    @classmethod
    def get_cached_data(cls):
        cd = cache.get("qun-cat")
        if not cd:
            qd = (
                cls.get_queryset(is_active=0)
                .order_by("order_of")
                .values_list("code", "name")
            )
            cache.set("qun-cat", list(qd))
            cd = cache.get("qun-cat")
        return cd


class TableHeader(AbstractModel):
    code = models.CharField(max_length=8, default=None)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class TableAttribute(AbstractModel):
    code = models.CharField(max_length=16, blank=True, default=None)
    name = models.CharField(max_length=128)
    tbl_header = models.ForeignKey(
        TableHeader, null=True, on_delete=models.SET_NULL)
    short_name = models.CharField(max_length=64, blank=True, default=None)

    def __str__(self):
        if not self.short_name:
            return f"{self.name}-{self.tbl_header}"
        return f"{self.short_name}-{self.tbl_header}"


class TableName(AbstractModel):
    code = models.CharField(max_length=8, default=None)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class RuleEngine(AbstractModel):
    tbl_attribute = models.ForeignKey(
        TableAttribute, null=True,
        on_delete=models.SET_NULL, verbose_name="field name"
    )
    tbl_attribute_type = models.ForeignKey(
        TableHeader, null=True,
        on_delete=models.SET_NULL, verbose_name="field type"
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.SET_NULL, null=True, verbose_name="chapter"
    )
    # 11 => one to one, 112=> one to many
    relationship = models.PositiveSmallIntegerField(
        default=11, verbose_name="relationship", choices=RELATIONSHIP
    )
    pair_attr = models.ForeignKey(
        TableAttribute,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="paired field name",
        related_name="pair_attr",
    )
    pair_attr_priority = models.PositiveSmallIntegerField(
        null=True, verbose_name="order by pair attribute", default=None
    )

    # 2 => addition, 3=> subtraction, 0 => no operation.
    operation1 = models.PositiveSmallIntegerField(
        null=True, default=0, verbose_name="arithmetic1", choices=ARITHMETIC
    )
    tbl1 = models.ForeignKey(
        TableName,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Table1 Name",
        related_name="tbl1",
    )
    header1 = models.ForeignKey(
        TableHeader,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Header1 / Column1 Name",
        related_name="header1",
    )
    amount1 = models.PositiveSmallIntegerField(
        null=True,
        default=0,
        verbose_name="amount1 pair position from question",
        validators=[MaxValueValidator(9), MinValueValidator(0)],
    )
    help1 = models.CharField(
        max_length=1024, blank=True, verbose_name="information1")

    # 2 => addition, 3=> subtraction, 0 => no operation.
    operation2 = models.PositiveSmallIntegerField(
        null=True, default=0, verbose_name="arithmetic2", choices=ARITHMETIC
    )
    tbl2 = models.ForeignKey(
        TableName,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Table2 Name",
        related_name="tbl2",
    )
    header2 = models.ForeignKey(
        TableHeader,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Header2 / Column2 Name",
        related_name="header2",
    )
    amount2 = models.PositiveSmallIntegerField(
        null=True,
        default=0,
        verbose_name="amount2 pair position from question",
        validators=[MaxValueValidator(9), MinValueValidator(0)],
    )
    help2 = models.CharField(
        max_length=1024, blank=True, verbose_name="information2")

    # 2 => addition, 3=> subtraction, 0 => no operation.
    operation3 = models.PositiveSmallIntegerField(
        null=True, default=0, verbose_name="arithmetic3", choices=ARITHMETIC
    )
    tbl3 = models.ForeignKey(
        TableName,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Table3 Name",
        related_name="tbl3",
    )
    header3 = models.ForeignKey(
        TableHeader,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Header3 / Column3 Name",
        related_name="header3",
    )
    amount3 = models.PositiveSmallIntegerField(
        null=True,
        default=0,
        verbose_name="amount3 pair position from question",
        validators=[MaxValueValidator(9), MinValueValidator(0)],
    )
    help3 = models.CharField(
        max_length=1024, blank=True, verbose_name="information3")

    # for jr inter ch7 had 4 place to move single element
    # 2 => addition, 3=> subtraction, 0 => no operation.
    operation4 = models.PositiveSmallIntegerField(
        null=True, blank=True, default=0, verbose_name="arithmetic4",
        choices=ARITHMETIC
    )
    tbl4 = models.ForeignKey(
        TableName,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Table4 Name",
        related_name="tbl4",
    )
    header4 = models.ForeignKey(
        TableHeader,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Header4 / Column4 Name",
        related_name="header4",
    )
    amount4 = models.PositiveSmallIntegerField(
        null=True,
        default=0,
        verbose_name="amount4 pair position from question",
        validators=[MaxValueValidator(9), MinValueValidator(0)],
    )
    help4 = models.CharField(
        max_length=1024, blank=True, verbose_name="information4")

    def __str__(self):
        try:
            return f"{self.tbl_attribute.name} - {self.is_active}"
        except Exception as e:
            print(e.__str__())
            return "n/a"

    @property
    def attribute_name(self):
        try:
            return self.tbl_attribute.name
        except Exception as e:
            print(e.__str__())
            return "n/a"

    @property
    def rel_name(self):
        # 11 => one to one, 112=> one to many
        return RELATIONSHIP_DICT.get(self.relationship, "...")
        # return '1to1' if self.relationship == 11 else '1to..'

    @property
    def pair_att_with(self):
        if not self.pair_attr:
            return None
        return self.pair_attr.name

    @property
    def opt1(self):
        return self.operation1

    @property
    def tbl1_name(self):
        if not self.tbl1:
            return None
        return self.tbl1.name

    @property
    def header1_name(self):
        if not self.header1:
            return None
        return self.header1.name

    @property
    def opt2(self):
        return self.operation2

    @property
    def tbl2_name(self):
        if not self.tbl2:
            return None
        return self.tbl2.name

    @property
    def header2_name(self):
        if not self.header2:
            return None
        return self.header2.name

    @property
    def tbl1_data(self):
        return {
            "tbl": self.tbl1,
            "header": self.header1,
            "operation": self.operation1,
            "pair": self.pair_attr.code,
            "order": self.pair_attr_priority,
            "help": self.help1,
        }

    @property
    def tbl2_data(self):
        if not self.tbl2:
            return None

        return {
            "tbl": self.tbl2,
            "header": self.header2,
            "operation": self.operation2,
            "pair": self.pair_attr.code,
            "order": self.pair_attr_priority,
            "help": self.help2,
        }

    @property
    def tbl3_data(self):
        if not self.tbl3:
            return None

        return {
            "tbl": self.tbl3,
            "header": self.header3,
            "operation": self.operation3,
            "pair": self.pair_attr.code,
            "order": self.pair_attr_priority,
            "help": self.help3,
        }

    @classmethod
    def validate_table(cls, particular, tbl_code):
        attribute = particular.attribute
        chapter = particular.exam.chapter
        # _chapter_code = chapter.code

        rule = (
            cls.get_queryset(tbl_attribute=attribute, chapter=chapter)
            .select_related(
                "tbl_attribute",
                "tbl_attribute_type",
                "chapter",
                "pair_attr",
                "tbl1",
                "header1",
                "tbl2",
                "header2",
            )
            .first()
        )

        if not rule:
            return False, [{"error": "invalid rule."}]

        if rule.tbl1.code == tbl_code:
            return True, [{}]
        elif rule.tbl2.code == tbl_code:
            return True, [{}]
        elif rule.tbl3 and rule.tbl3.code == tbl_code:
            return True, [{}]
        else:
            _help = f"1. {rule.help1}"

            if rule.help2:
                _help += f" \n 2. {rule.help2}"

            if rule.help3:
                _help += f" \n 2. {rule.help3}"

            return False, [{"error": "Invalid", "help": _help}]

    @classmethod
    def dummy_def(cls, *args, **kwargs):
        return False, [{"error": "invalid chapter 009"}]

    @classmethod
    def validate_answer(
        cls,
        particular,
        tbl_code,
        particular_code,
        add_sub,
        user,
        action,
        amount,
        position=0,
    ):
        """
        Check answer with rule engine.

        :param particular:
        :param tbl_code:
        :param particular_code:
        :param add_sub:
        :param user:
        :param action:
        :param amount:
        :param position:
        :return:
        """
        attribute = particular.attribute
        chapter = particular.exam.chapter
        _chapter_code = chapter.code

        rule = (
            cls.get_queryset(tbl_attribute=attribute, chapter=chapter)
            .select_related(
                "tbl_attribute",
                "tbl_attribute_type",
                "chapter",
                "pair_attr",
                "tbl1",
                "header1",
                "tbl2",
                "header2",
            )
            .first()
        )

        if not rule:
            return False, [{"error": "invalid rule."}]

        is_valid, msg = False, [{"error": "Mr. 007 invalid action"}]

        if not action.startswith("auto"):

            _chapter = dict(
                ch1=cls.validate_ans_ch1,
                ch2=cls.validate_ans_ch2,
                ch3=cls.validate_ans_ch3,
                ch4=cls.validate_ans_ch3,
                ch5=cls.validate_ans_ch3,
                ch6=cls.validate_ans_ch3,
            )
            is_valid, msg = _chapter.get(_chapter_code, cls.dummy_def)(
                rule, tbl_code, particular_code, add_sub, position=position
            )

        elif action.startswith("auto"):
            _a, tbl, particular_ui, add_sub = action.split("#")
            _d = dict()
            _d[rule.tbl1.code] = rule.tbl1_data

            if rule.tbl2:
                _d[rule.tbl2.code] = rule.tbl2_data
            if rule.tbl3:
                _d[rule.tbl3.code] = rule.tbl3_data

            # overwrite input and force get data of ch1
            if _chapter_code in (
                "ch1",
                "ch2",
            ):
                is_valid, msg = True, list(_d.values())
            else:
                is_valid, msg = True, [_d.get(tbl)]

                # if tbl not found in rule?
                if not _d.get(tbl):
                    is_valid, msg = False, [{"error": "invalid action #382"}]

        if not is_valid:
            return False, msg

        from answer.models import ExamAnswer

        for row in msg:
            tbl_name = row.get("tbl")
            tbl_header = row.get("header")
            operation = row.get("operation")

            try:
                ExamAnswer.answer_save(
                    user,
                    particular,
                    rule,
                    tbl_name,
                    tbl_header,
                    attribute,
                    amount,
                    operation,
                )
                row["operation"] = ARITHMETIC_DICT.get(operation)

            except IntegrityError as ie:
                """
                 mysql error:
                 django.db.utils.IntegrityError(1062,
                "Duplicate entry '1-971-20-1-181' for key
                'answer_examanswer_user_id_qun_id_tbl_name__347ba51a_uniq'")
                """

                if ie.__str__().find("Duplicate") > -1:
                    return False, [{"error": "already answered"}]
                return False, [{"error": ie.__str__()}]

            except Exception as e:

                return False, [{"error": e.__str__()}]

        return is_valid, msg

    @classmethod
    def validate_ans_ch1(
            cls, rule, tbl_code, particular_code, add_sub, **kwargs):
        """
        validate chapter 1 rules
        :param rule:
        :param tbl_code:
        :param particular_code:
        :param add_sub:
        :return:
        """
        # one to one relationship rule.
        # has to look for only tbl1 and header1
        _help = rule.help1
        _tbl1 = (rule.tbl1.code, rule.header1.code, rule.operation1)
        opt = ARITHMETIC_BY_VALUE.get(add_sub)
        _values = (tbl_code, particular_code, opt)

        if _tbl1 == _values:
            return True, [
                {
                    "tbl": rule.tbl1,
                    "header": rule.header1,
                    "operation": rule.operation1,
                    "pair": rule.pair_attr.code,
                    "order": rule.pair_attr_priority,
                    "help": _help,
                }
            ]

        return False, [{"error": "Invalid", "help": _help}]

    @classmethod
    def validate_ans_ch2(
            cls, rule, tbl_code, particular_code, add_sub, **kwargs):
        """
        validate chapter 2 rules
        :param rule:
        :param tbl_code:
        :param particular_code:
        :param add_sub:
        :param kwargs:
        :return:
        """
        # one to two relationship rule.
        # has to look for only tbl1, header1, help1, tbl2, header2 and help2

        """
        table1 rule or table2 rule or table3 rule?
        """
        _tbl1 = (rule.tbl1.code, rule.header1.code, rule.operation1)
        _tbl2 = None
        if rule.tbl2 and rule.header2 and rule.operation2:
            _tbl2 = (rule.tbl2.code, rule.header2.code, rule.operation2)

        opt = ARITHMETIC_BY_VALUE.get(add_sub)
        _values = (tbl_code, particular_code, opt)
        _help = f"1. {rule.help1}"

        if _tbl1 == _values:
            return True, [
                {
                    "tbl": rule.tbl1,
                    "header": rule.header1,
                    "operation": rule.operation1,
                    "pair": rule.pair_attr.code,
                    "order": rule.pair_attr_priority,
                }
            ]

        if rule.help2:
            _help += f" \n 2. {rule.help2}"

        if _tbl2 and _tbl2 == _values:
            return True, [
                {
                    "tbl": rule.tbl2,
                    "header": rule.header2,
                    "operation": rule.operation2,
                    "pair": rule.pair_attr.code,
                    "order": rule.pair_attr_priority,
                    "help": _help,
                }
            ]

        return False, [{"error": "Invalid", "help": _help}]

    @classmethod
    def validate_ans_ch3(
            cls, rule, tbl_code, particular_code, add_sub, **kwargs):
        _position = int(kwargs.get("position", 1))
        _tbl1 = (
            rule.tbl1.code, rule.header1.code, rule.operation1, rule.amount1)
        _tbl2 = None
        _tbl3 = None
        if rule.tbl2 and rule.header2 and rule.operation2:
            _tbl2 = (
                rule.tbl2.code, rule.header2.code,
                rule.operation2, rule.amount2)

        if rule.tbl3 and rule.header3 and rule.operation3:
            _tbl3 = (
                rule.tbl3.code, rule.header3.code,
                rule.operation3, rule.amount3)

        opt = ARITHMETIC_BY_VALUE.get(add_sub)
        _values = (tbl_code, particular_code, opt, _position)
        _help = f"1. {rule.help1}"

        if _tbl1 == _values:
            return True, [
                {
                    "tbl": rule.tbl1,
                    "header": rule.header1,
                    "operation": rule.operation1,
                    "pair": rule.pair_attr.code,
                    "order": rule.pair_attr_priority,
                    "help": _help,
                }
            ]

        if rule.help2:
            _help += f" \n 2. {rule.help2}"

        if _tbl2 and _tbl2 == _values:
            return True, [
                {
                    "tbl": rule.tbl2,
                    "header": rule.header2,
                    "operation": rule.operation2,
                    "pair": rule.pair_attr.code,
                    "order": rule.pair_attr_priority,
                    "help": _help,
                }
            ]

        if rule.help3:
            _help += f" \n 3. {rule.help3}"

        if _tbl3 and _tbl3 == _values:
            return True, [
                {
                    "tbl": rule.tbl3,
                    "header": rule.header3,
                    "operation": rule.operation3,
                    "pair": rule.pair_attr.code,
                    "order": rule.pair_attr_priority,
                    "help": _help,
                }
            ]

        return False, [{"error": "Invalid", "help": _help}]

    @classmethod
    def get_list_ans_table(cls, attribute, chapter):
        return cls.get_queryset(
            tbl_attribute__in=attribute, chapter=chapter
        ).select_related("tbl1", "tbl2", "tbl3")

    @classmethod
    def get_set_of_tbl_header(cls, attribute, chapter):
        return cls.get_queryset(
            tbl_attribute=attribute, chapter=chapter
        ).select_related("header1", "header2", "header3", "header4")


class State(AbstractModel):
    code = models.CharField(max_length=8, default=code_generator)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
