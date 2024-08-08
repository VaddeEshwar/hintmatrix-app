import json

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from account.models import Profile
from answer.models import AnswerEvent
from config.models import RuleEngine, QuestionCategory
from question.models import ExamQuestion
from utils.message.shoot_email_support import shoot_forgot_password_email


def prepare_table_object_key(tbl, amount):
    return f"{tbl.name}-{tbl.code}-{amount}"


def prepare_table_object(tbl, amount):
    return {"name": tbl.name, "code": tbl.code, "amount": amount}


class ProfileModelForm(forms.ModelForm):
    user = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Profile
        fields = ["mobile", "is_wa_number", "address", "state"]


class ForgotEmailForm(forms.Form):
    email = forms.EmailField(max_length=80)

    def clean(self):
        cleaned_data = super(ForgotEmailForm, self).clean()
        """
        1. get email
        2. check from db
        3. send email to same email for validation.
        4. click on link, will land at set-forgot-password url.
        """
        email = cleaned_data["email"]
        user = User.objects.filter(username=email)
        if user.exists():
            user = user.first()
            try:
                if not shoot_forgot_password_email(user):
                    print(f"Forgot email not able to send {user.email}.")
                else:
                    print(f"Forgot email able sent to {user.email}.")
            except Exception as e:
                print(40, e.__str__())
                raise

        return cleaned_data


class V2ExamTableForm(forms.Form):
    slug = forms.SlugField(
        widget=forms.TextInput(attrs={"placeholder": "slug"}))
    error = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(V2ExamTableForm, self).clean()
        cleaned_data["upon"] = "tbl2"
        cleaned_data["table"] = []

        slug = cleaned_data.get("slug")

        qun_attr = ExamQuestion.get_queryset(
            slug=slug.__str__()
        ).first()  # .select_related("tbl1", "tbl2", "tbl3")

        if not qun_attr:
            raise forms.ValidationError({"error": "invalid answer"})

        attribute = qun_attr.attribute

        # extra DB call to avoid.
        if self.initial.get("chapter_code") in {"ch4", "ch6"}:
            """
            for ch4 n 6, we have to sent no of dr and cr accounts and list 
            of available accounts to show in drop down.
            """
            attr_rule = list(RuleEngine.get_set_of_tbl_header(
                attribute=attribute,
                chapter=qun_attr.exam.chapter).values(
                "header1__code", "header2__code",
                "header3__code", "header4__code"))

            res = list(attr_rule[0].values())
            header_wise_count = {
                "dr": res.count("dr"),
                "cr": res.count("cr")
            }
            # header_wise_count = {i: res.count(i) for i in res if i}

            all_attribute = qun_attr.get_queryset(
                exam=qun_attr.exam).values("attribute_id")
            rules = RuleEngine.get_list_ans_table(
                all_attribute, qun_attr.exam.chapter)

            if not rules:
                raise forms.ValidationError(
                    {"error": "solution not found. 64"})

            table_dict = {}
            for rule in rules:
                table_dict[
                    prepare_table_object_key(rule.tbl1, rule.amount1)
                ] = prepare_table_object(rule.tbl1, rule.amount1)

                table_dict[
                    prepare_table_object_key(rule.tbl2, rule.amount2)
                ] = prepare_table_object(rule.tbl2, rule.amount2)

                if rule.tbl3:
                    table_dict[
                        prepare_table_object_key(rule.tbl3, rule.amount3)
                    ] = prepare_table_object(rule.tbl3, rule.amount3)
                    cleaned_data["upon"] = "tbl3"

            cleaned_data["table"] = list(table_dict.values())
            cleaned_data["header_cnt"] = header_wise_count

        else:
            rule = RuleEngine.get_list_ans_table(
                [attribute], qun_attr.exam.chapter
            ).first()

            if not rule:
                raise forms.ValidationError(
                    {"error": "solution not found. 86"})

            cleaned_data["table"] = [
                prepare_table_object(rule.tbl1, rule.amount1),
                prepare_table_object(rule.tbl2, rule.amount2),
            ]

            if rule.tbl3:
                cleaned_data["table"].append(
                    prepare_table_object(rule.tbl3, rule.amount3)
                )
                cleaned_data["upon"] = "tbl3"

        return cleaned_data


def v2_answer_step1(request, particular, tbl_code, cleaned_data):
    """
    :param request:
    :param particular:
    :param tbl_code:
    :param cleaned_data:
    :return:
    1. Chosen table is valid for table attribute.
    2. if not return help.
    """
    is_valid, msg = RuleEngine.validate_table(
        particular=particular, tbl_code=tbl_code)
    # print(request, cleaned_data)
    _history = []
    _event = AnswerEvent.add_event(
        tbl_code,
        particular.attribute.code,
        None,
        particular,
        request.user,
        is_valid,
        "step1",
        hint=msg[0].get("help", "step1-n/a"),
    )
    _history.append(
        {
            "description": _event.description,
            "valid": _event.valid,
            "action": _event.action,
        }
    )
    msg[0]["history"] = json.dumps(_history)
    return is_valid, msg


class V2AnswerFrom(forms.Form):
    action = forms.CharField(
        max_length=20, widget=forms.TextInput(
            attrs={"placeholder": "Action"})
    )
    slug = forms.SlugField(widget=forms.TextInput(
        attrs={"placeholder": "slug"}))
    qun_slug = forms.SlugField(
        widget=forms.TextInput(attrs={"placeholder": "qun slug"})
    )
    amount = forms.FloatField(
        required=False, widget=forms.TextInput(
            attrs={"placeholder": "amount"})
    )
    position = forms.IntegerField(required=False)

    error = forms.CharField(required=False, widget=forms.HiddenInput())
    help = forms.CharField(required=False, widget=forms.HiddenInput())
    history = forms.CharField(required=False, widget=forms.HiddenInput())
    pair = forms.CharField(required=False, widget=forms.HiddenInput())
    order = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(V2AnswerFrom, self).clean()

        request = self.initial["request"]
        action = cleaned_data.get("action")

        slug = cleaned_data.get("slug")
        qun_slug = cleaned_data.get("qun_slug")
        position = cleaned_data.get("position", 1)

        qun_attr = (
            ExamQuestion.get_queryset(
                slug=slug.__str__(), exam__slug=qun_slug.__str__()
            )
            .select_related("exam", "tbl_header", "attribute")
            .first()
        )

        if not qun_attr:
            raise forms.ValidationError({"error": "invalid answer"})

        amount = cleaned_data.get("amount")
        if not amount:
            amount = qun_attr.amount
            cleaned_data["amount"] = amount

        tbl, particular, add_sub = (None, None, None)
        if not action:
            raise forms.ValidationError({"error": "invalid action #70"})

        if action.startswith("step1"):
            act, tbl_code = action.split("#")
            is_valid, msg = v2_answer_step1(
                request, qun_attr, tbl_code, cleaned_data)
            if not is_valid:
                raise forms.ValidationError(msg[0])
            return dict()

        if not action.startswith("auto"):
            tbl, particular, add_sub = action.split("#")

        is_valid, msg = RuleEngine.validate_answer(
            qun_attr, tbl, particular, add_sub, request.user,
            action, amount, position
        )

        _history = []
        action1 = action if action.startswith("auto") else None

        if not is_valid:
            _event = AnswerEvent.add_event(
                table=tbl,
                particular=particular,
                add_sub=add_sub,
                exam_question=qun_attr,
                user=request.user,
                valid=is_valid,
                action=action1,
                hint=msg[0].get("help", "n/a"),
            )
            _history.append(
                {
                    "c_on": _event.c_on.__str__(),
                    "element": _event.qun.attribute.name,
                    "user_answer": _event.user_answer,
                    "valid": _event.valid,
                    "score": _event.score,
                    "answer_by": _event.answer_by,
                    "hint": _event.hint,
                }
            )
            msg[0]["history"] = json.dumps(_history)
            raise forms.ValidationError(msg[0])

        actions = []
        pair = ""
        order = 1
        tbl_name = ""
        for row in msg:
            _event = AnswerEvent.add_event(
                table=row["tbl"].code,
                particular=row["header"].code,
                add_sub=row["operation"],
                exam_question=qun_attr,
                user=request.user,
                valid=is_valid,
                action=action1,
                hint=row.get("help", "n/a"),
            )
            _history.append(
                {
                    "c_on": _event.c_on.__str__(),
                    "element": _event.qun.attribute.name,
                    "user_answer": _event.user_answer,
                    "valid": _event.valid,
                    "score": _event.score,
                    "answer_by": _event.answer_by,
                    "hint": _event.hint,
                }
            )

            actions.append(
                f'{row["tbl"].code}#{row["header"].code}#{row["operation"]}')

            pair = row["pair"]
            order = row["order"]
            tbl_name = row["tbl"].name

        cleaned_data["pair"] = pair
        cleaned_data["order"] = order
        cleaned_data["action"] = actions
        cleaned_data["tbl_name"] = tbl_name
        cleaned_data["history"] = json.dumps(_history)
        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(
        label="Email Or Username", max_length=254)


class QuestionForm(forms.Form):
    name = forms.CharField(
        max_length=500, widget=forms.Textarea(
            attrs={"placeholder": "Question"})
    )
    question_code = forms.CharField(
        max_length=16,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "Question order by serial code"}),
    )
    question_category = forms.ModelChoiceField(
        queryset=None,
        blank=False,
        empty_label="-- Please choose question category option--",
    )
    sel_debit_balance = forms.ModelChoiceField(
        queryset=None, blank=False, empty_label="-- Please choose DR option--"
    )
    txt_debit_balance = forms.FloatField(min_value=0)
    sel_credit_balance = forms.ModelChoiceField(
        queryset=None, blank=False, empty_label="-- Please choose CR option--"
    )
    txt_credit_balance = forms.FloatField(min_value=0)

    sel_adjustment = forms.ModelChoiceField(
        queryset=None, blank=True, empty_label="-- Please choose ADJ option--"
    )
    txt_adjustment_balance = forms.FloatField(min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chapter_code = kwargs.get("initial").get("chapter_code")

        qun_category = QuestionCategory.get_queryset(
            is_active=1).order_by("order_of")

        debit_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="debit particulars",
            is_active=0,
            chapter__code=chapter_code,
        ).order_by("tbl_attribute__name")
        credit_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="credit particulars",
            is_active=0,
            chapter__code=chapter_code,
        ).order_by("tbl_attribute__name")
        adjustment_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="adjustments",
            is_active=0,
            chapter__code=chapter_code,
        ).order_by("tbl_attribute__name")

        self.fields["question_category"].choices = [
            ("", "-- Please choose Question Category option--"),
        ] + [(row.id, row.name) for row in qun_category]
        self.fields["sel_debit_balance"].choices = [
            ("", "-- Please choose DR option--"),
        ] + [(row.tbl_attribute_id, row.tbl_attribute.name
              ) for row in debit_attributes]
        self.fields["sel_debit_balance"].widget.attrs.update(
            **{"class": "select-one"})
        self.fields["txt_debit_balance"].widget.attrs.update(
            **{"class": "inp-num"})
        self.fields["sel_credit_balance"].choices = [
            ("", "-- Please choose CR option--"),
        ] + [
            (row.tbl_attribute_id, row.tbl_attribute.name
             ) for row in credit_attributes
        ]
        self.fields["sel_credit_balance"].widget.attrs.update(
            **{"class": "select-one"})
        self.fields["txt_credit_balance"].widget.attrs.update(
            **{"class": "inp-num"})
        self.fields["sel_adjustment"].choices = [
            ("", "-- Please choose ADJ option--"),
        ] + [
            (row.tbl_attribute_id, row.tbl_attribute.name)
            for row in adjustment_attributes
        ]
        self.fields["sel_adjustment"].widget.attrs.update(
            **{"class": "select-one"})
        self.fields["txt_adjustment_balance"].widget.attrs.update(
            **{"class": "inp-num"}
        )


class QuestionCh3Form(forms.Form):
    name = forms.CharField(
        max_length=500, widget=forms.Textarea(
            attrs={"placeholder": "Question"})
    )
    question_code = forms.CharField(
        max_length=16,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "Question order by serial code"}),
    )
    question_category = forms.ModelChoiceField(
        queryset=None,
        blank=False,
        empty_label="-- Please choose question category option--",
    )
    sel_journal_balance = forms.ModelChoiceField(
        queryset=None, blank=False, empty_label="-- Please choose JR option--"
    )
    txt_balance1 = forms.FloatField(min_value=0)
    txt_balance2 = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chapter_code = kwargs.get("initial").get("chapter_code")

        qun_category = QuestionCategory.get_queryset(
            is_active=1).order_by("order_of")
        journal_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="transaction",
            chapter__code=chapter_code,
            is_active=0,
        ).order_by("tbl_attribute__name")

        self.fields["question_category"].choices = [
            ("", "-- Please choose Question Category option--"),
        ] + [(row.id, row.name) for row in qun_category]
        self.fields["sel_journal_balance"].choices = [
            ("", "-- Please choose JR option--"),
        ] + [(row.tbl_attribute_id, row.tbl_attribute
              ) for row in journal_attributes]
        self.fields["sel_journal_balance"].widget.attrs.update(
            **{"class": "select-one"}
        )
        self.fields["txt_balance1"].widget.attrs.update(
            **{"class": "inp-num"})
        self.fields["txt_balance2"].widget.attrs.update(
            **{"class": "inp-num"})


class QuestionCh4Form(forms.Form):
    name = forms.CharField(
        max_length=500, widget=forms.Textarea(
            attrs={"placeholder": "Question"})
    )
    question_code = forms.CharField(
        max_length=16,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "Question order by serial code"}),
    )
    question_category = forms.ModelChoiceField(
        queryset=None,
        blank=False,
        empty_label="-- Please choose question category option--",
    )
    sel_journal_balance = forms.ModelChoiceField(
        queryset=None, blank=False, empty_label="-- Please choose JR option--"
    )
    txt_balance1 = forms.FloatField(min_value=0)
    txt_balance2 = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chapter_code = kwargs.get("initial").get("chapter_code")

        qun_category = QuestionCategory.get_queryset(
            is_active=1).order_by("order_of")

        journal_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="transaction",
            chapter__code=chapter_code,
            is_active=0,
        ).order_by("tbl_attribute__name")

        self.fields["question_category"].choices = [
            ("", "-- Please choose Question Category option--"),
        ] + [(row.id, row.name) for row in qun_category]
        self.fields["sel_journal_balance"].choices = [
            ("", "-- Please choose JR option--"),
        ] + [(row.tbl_attribute_id, row.tbl_attribute
              ) for row in journal_attributes]
        self.fields["sel_journal_balance"].widget.attrs.update(
            **{"class": "select-one"}
        )
        self.fields["txt_balance1"].widget.attrs.update(**{"class": "inp-num"})
        self.fields["txt_balance2"].widget.attrs.update(**{"class": "inp-num"})


class QuestionCh5Form(forms.Form):
    name = forms.CharField(
        max_length=500, widget=forms.Textarea(
            attrs={"placeholder": "Question"})
    )
    question_code = forms.CharField(
        max_length=16,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "Question order by serial code"}),
    )
    question_category = forms.ModelChoiceField(
        queryset=None,
        blank=False,
        empty_label="-- Please choose question category option--",
    )
    sel_journal_balance = forms.ModelChoiceField(
        queryset=None, blank=False, empty_label="-- Please choose JR option--"
    )
    txt_balance1 = forms.FloatField(min_value=0)
    txt_balance2 = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qun_category = QuestionCategory.get_queryset(
            is_active=1).order_by("order_of")
        journal_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="transaction",
            chapter__code="ch5", is_active=0
        ).order_by("tbl_attribute__name")

        self.fields["question_category"].choices = [
            ("", "-- Please choose Question Category option--"),
        ] + [(row.id, row.name) for row in qun_category]
        self.fields["sel_journal_balance"].choices = [
            ("", "-- Please choose JR option--"),
        ] + [(row.tbl_attribute_id, row.tbl_attribute
              ) for row in journal_attributes]
        self.fields["sel_journal_balance"].widget.attrs.update(
            **{"class": "select-one"}
        )
        self.fields["txt_balance1"].widget.attrs.update(**{"class": "inp-num"})
        self.fields["txt_balance2"].widget.attrs.update(**{"class": "inp-num"})


class QuestionCh6Form(forms.Form):
    name = forms.CharField(
        max_length=500, widget=forms.Textarea(
            attrs={"placeholder": "Question"})
    )
    question_code = forms.CharField(
        max_length=16,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "Question order by serial code"}),
    )
    question_category = forms.ModelChoiceField(
        queryset=None,
        blank=False,
        empty_label="-- Please choose question category option--",
    )
    sel_journal_balance = forms.ModelChoiceField(
        queryset=None, blank=False, empty_label="-- Please choose JR option--"
    )
    txt_balance1 = forms.FloatField(min_value=0)
    txt_balance2 = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chapter_code = kwargs.get("initial").get("chapter_code")

        qun_category = QuestionCategory.get_queryset(
            is_active=1).order_by("order_of")

        journal_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="transaction",
            chapter__code=chapter_code,
            is_active=0,
        ).order_by("tbl_attribute__name")

        self.fields["question_category"].choices = [
            ("", "-- Please choose Question Category option--"),
        ] + [(row.id, row.name) for row in qun_category]
        self.fields["sel_journal_balance"].choices = [
            ("", "-- Please choose JR option--"),
        ] + [(row.tbl_attribute_id, row.tbl_attribute
              ) for row in journal_attributes]
        self.fields["sel_journal_balance"].widget.attrs.update(
            **{"class": "select-one"}
        )
        self.fields["txt_balance1"].widget.attrs.update(**{"class": "inp-num"})
        self.fields["txt_balance2"].widget.attrs.update(**{"class": "inp-num"})


class QuestionCh7Form(forms.Form):
    name = forms.CharField(
        max_length=500, widget=forms.Textarea(
            attrs={"placeholder": "Question"})
    )
    question_code = forms.CharField(
        max_length=16,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "Question order by serial code"}),
    )
    question_category = forms.ModelChoiceField(
        queryset=None,
        blank=False,
        empty_label="-- Please choose question category option--",
    )
    tr_date = forms.DateField(widget=forms.DateInput(
        attrs={"type": "date"})
    )
    sel_journal_balance = forms.ModelChoiceField(
        queryset=None, blank=False, empty_label="-- Please choose Ledger TR --"
    )
    txt_balance1 = forms.FloatField(min_value=0)
    txt_balance2 = forms.FloatField(required=False)
    ext_jf_lf = forms.CharField(
        required=False,
        max_length=2,
        min_length=1,
        widget=forms.TextInput(
            attrs={"placeholder": "JF"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chapter_code = kwargs.get("initial").get("chapter_code")

        qun_category = QuestionCategory.get_queryset(
            is_active=1).order_by("order_of")

        journal_attributes = RuleEngine.get_queryset(
            tbl_attribute_type__name="transaction",
            chapter__code=chapter_code,
            is_active=0,
        ).order_by("tbl_attribute__name")

        self.fields["question_category"].choices = [
            ("", "-- Please choose Question Category option--"),
        ] + [(row.id, row.name) for row in qun_category]

        self.fields["sel_journal_balance"].choices = [
            ("", "-- Please choose Ledger option--"),
        ] + [(row.tbl_attribute_id, row.tbl_attribute
              ) for row in journal_attributes]

        self.fields["sel_journal_balance"].widget.attrs.update(
            **{"class": "select-one"}
        )

        self.fields["txt_balance1"].widget.attrs.update(**{"class": "inp-num"})
        self.fields["txt_balance2"].widget.attrs.update(**{"class": "inp-num"})


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "name": "username",
                "autocomplete": "off",
                "placeholder": "Username",
                "required": "required",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        max_length=30,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "name": "password",
                "placeholder": "Password",
                "required": "required",
            }
        ),
    )


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.pop("confirm_password", "")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match")
        return cleaned_data
