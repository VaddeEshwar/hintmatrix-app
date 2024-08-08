import logging
from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View

from account.models import Profile, SubscriptionPermission
from answer.models import AnswerEvent, ExamAnswer
from config.models import Chapter, QuestionCategory, RuleEngine, TableHeader
from question.models import Exam, ExamQuestion
from shop.models import Product, PurchaseOrder
from utils.api_utils import render_api_response
from utils.cash_free_pg import pg_order_create
from utils.generate_key import id_generator
from utils.streaming_csv_response import streaming_zip_view
from utils.views import zip_cycle
from website.forms import (
    ProfileModelForm,
    QuestionCh3Form,
    QuestionCh4Form,
    QuestionCh5Form,
    QuestionCh6Form,
    QuestionCh7Form,
    QuestionForm,
    V2AnswerFrom,
    V2ExamTableForm,
)

logger = logging.getLogger(__name__)


def check_profile(view_func):
    """
    Decorator that adds subscription permissions to a request so that it
    will execute properly.
    """

    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        user = request.request.user
        # fix profile
        instance = Profile.get_queryset(user=user).first()
        if not instance:
            return redirect("website_v2:my-profile")

        setattr(request.request.user, "profile", instance)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


def check_subscription(view_func):
    """
    Decorator that adds subscription permissions to a request so that it
    will execute properly.
    """

    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        subscription = getattr(request.request.user, "subscription", None)
        if not subscription:
            # set request.permissions
            # get permission from DB
            # cache permission for faster access
            sub_permissions = SubscriptionPermission.get_queryset(
                user=request.request.user, valid_to__gte=timezone.now().date()
            ).select_related("product")

            if not sub_permissions.exists():
                # redirect to subscription page
                return redirect("website_v2:course-subscribe-1")

            # print(sub_permissions)
            pc = sub_permissions.values_list("product__code", "product__days")
            # {'fyoy': 365, 'fyom': 30, 'fyow': 7}
            # check subscription permissions for chapter.
            pc = dict(pc)
            setattr(request.request.user, "subscription", sub_permissions)

            is_trail = False if 7 < max(pc.values()) else True
            setattr(request.request.user, "is_trail", is_trail)

        # if validity < 8: only fetch 2 questions
        # else all
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


def check_permission(view_func):
    """
    Decorator that adds subscription permissions to a request so that it
    will execute properly.
    """

    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        # set request.permissions
        # get permission from DB
        # cache permission for faster access
        if not kwargs.get("chapter_code"):
            return view_func(request, *args, **kwargs)

        _has = SubscriptionPermission.has_permission(
            user=request.request.user, chapter_code=kwargs.get("chapter_code")
        )

        if not _has.exists():
            # redirect to subscription page
            return redirect("website_v2:course-subscribe-1")

        pc = _has.values_list("product__code", "product__days")
        # {'fyoy': 365, 'fyom': 30, 'fyow': 7}
        # check subscription permissions for chapter.
        pc = dict(pc)
        # setattr(request.request.user, "subscription", _has)

        is_trail = False if 7 < max(pc.values()) else True
        setattr(request.request.user, "is_trail", is_trail)

        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


class MyReferenceView(LoginRequiredMixin, View):
    requires_login = True
    login_url = "/login/?i=mc"

    permission_checker = None

    template_name = "v3/secure/my-reference.html"
    tabs = None

    @check_profile
    def get(self, *args, **kwargs):
        referral_code = (
            self.request.user.profile.get_reference_code.referral_code
        )
        http = "https" if self.request.is_secure() else "http"
        ref_url = (
                f"{http}://"
                + self.request.META.get("HTTP_HOST")
                + reverse("website_v2:signup")
                + f"?ref={referral_code}"
        )

        referrals = self.request.user.profile.reference_data
        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class MyProfileView(LoginRequiredMixin, View):
    requires_login = True
    login_url = "/login/?i=mc"

    permission_checker = None

    template_name = "v3/secure/my-profile.html"
    tabs = None

    def get(self, *args, **kwargs):
        user = self.request.user
        instance = Profile.get_queryset(user=user).first()
        pf = ProfileModelForm(instance=instance)

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )

    def post(self, *args, **kwargs):
        user = self.request.user
        instance = Profile.get_queryset(user=user).first()
        pf = ProfileModelForm(self.request.POST, instance=instance)

        if not pf.is_valid():
            errors = pf.errors
        else:
            pf_frm = pf.save(commit=False)
            if not pf_frm.user:
                pf_frm.user = user
            pf_frm.save()
            success = True

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class MyCourseView(LoginRequiredMixin, View):
    requires_login = True
    login_url = "/login/?i=mc"

    permission_checker = None

    template_name = "v3/secure/my-course.html"
    tabs = None

    @check_profile
    @check_subscription
    def get(self, *args, **kwargs):
        # get details from permission table and display.
        subscription = self.request.user.subscription
        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class CourseSubscriptionView(LoginRequiredMixin, View):
    requires_login = True
    login_url = "/login/?i=cs"

    permission_checker = None

    template_name = "v3/secure/subscriptions.html"
    tabs = None

    @check_profile
    def get(self, *args, **kwargs):
        course = kwargs.get("course")
        # /my-app/course-subscribe/
        if not course:
            products = Product.get_queryset(is_active=1)
        else:
            product = Product.get_queryset(slug=course)
            step1 = "step1"
            # /my-app/course-subscribe/<uuid>/
            if not product.exists():
                # invalid <uuid>, means user did not chose valid product to
                # buy.
                products = Product.get_queryset(is_active=1)
                step2 = "step2"
            else:
                step3 = "step3"
                # user choose valid product and about to purchase.
                product = product.first()
                # create purchase order
                # create order using cash free api.
                po, od = PurchaseOrder.create_order(
                    request=self.request,
                    user=self.request.user,
                    product=product,
                )

                if product.price < 1:
                    SubscriptionPermission.create_order(
                        self.request.user, po, product, trail=True
                    )

                    return redirect("website_v2:my-course")

                pg_order = pg_order_create(
                    order_id=po.slug.__str__(),
                    order_amount=po.total_cost,
                    order_note=po.note,
                    customer_id=self.request.user.id,
                    customer_email=self.request.user.email,
                    customer_phone=self.request.user.profile.mobile,
                    payment_for=po.name
                )
                # print(pg_order)

                # redirect to cash free payment link
                link_url = pg_order.get("link_url")
                print(link_url)
                logger.debug(f"link_url {link_url}")
                # print("$$$$$$$$$$")
                if link_url:
                    # payment link to purchase chosen product.
                    return redirect(link_url)
                else:
                    # Payment link not able to create. So, chose product again.
                    products = Product.get_queryset(is_active=1)

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class ToDoView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = True
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v2/secure/%s/copy-question.html"
    tabs = None

    def post(self, *args, **kwargs):
        question_slug = kwargs.get("question_slug")

        exam = Exam.get_queryset(slug=question_slug).first()
        rtn = {}
        if self.request.POST.get("action") == "delete":
            ExamAnswer.get_queryset(exam=exam).delete()
            ExamQuestion.get_queryset(exam=exam).delete()
            exam.delete()
            rtn["delete"] = "Successfully deleted"
        elif self.request.POST.get("action") == "enable":
            if exam.is_active:
                exam.is_active = False
                rtn["action"] = "disable"
            else:
                exam.is_active = True
                rtn["action"] = "enable"
            exam.save()

        return JsonResponse(rtn)


class CopyQuestionView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = True
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v2/secure/%s/copy-question.html"
    tabs = None

    def get(self, *args, **kwargs):
        question_slug = kwargs.get("question_slug")
        chapter_code = kwargs.get("chapter_code")

        exam = Exam.get_queryset(slug=question_slug).first()

        if chapter_code in (
                "ch4",
                "ch6",
        ):
            self.template_name = self.template_name % (chapter_code,)
            debit_balance = exam.get_ch4_transaction
            form = QuestionCh4Form(
                initial=dict(
                    chapter_code=chapter_code,
                    question_code=exam.question_code,
                    question_category=exam.question_category,
                )
            )
        elif chapter_code in (
                "ch3",
                "ch5",
        ):
            self.template_name = self.template_name % (chapter_code,)
            debit_balance = exam.get_ch3_transaction
            form = QuestionCh3Form(
                initial=dict(
                    chapter_code=chapter_code,
                    question_code=exam.question_code,
                    question_category=exam.question_category,
                )
            )
        elif chapter_code in (
                "ch1",
                "ch2",
        ):
            self.template_name = self.template_name % (chapter_code,)

            debit_balance = exam.get_debit_balance
            credit_balance = exam.get_credit_balance
            adjustments = exam.get_adjustment

            dr_cr = zip_cycle(debit_balance, credit_balance)

            form = QuestionForm(
                initial=dict(
                    question_code=exam.question_code,
                    question_category=exam.question_category,
                    chapter_code=chapter_code,
                )
            )

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class LogsView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v2/secure/logs.html"
    tabs = None

    @check_profile
    @check_subscription
    def get(self, request, *args, **kwargs):

        chapter_code = kwargs.get("chapter_code")
        slug = kwargs.get("slug")
        if not chapter_code:
            chapters = (
                AnswerEvent.get_queryset(user=self.request.user, valid=False)
                .exclude(exam__chapter__code=None)
                .values_list("exam__chapter__code", "exam__chapter__name")
                .order_by("exam__chapter__code")
                .distinct()
            )
        else:
            events = (
                AnswerEvent.get_queryset(
                    user=self.request.user,
                    exam__chapter__code=chapter_code
                )
                .exclude(valid=True)
                .select_related("qun")
                .order_by("-c_on")[:50]
            )
            question = events.first().exam

            self.template_name = "v2/secure/log-events.html"
        # elif slug:
        #     events = (
        #         AnswerEvent.get_queryset(
        #             user=self.request.user, exam__slug=slug
        #         )
        #         .exclude(valid=True)
        #         .select_related("qun")
        #         .order_by("-c_on")[:50]
        #     )
        #     question = events.first().exam
        #
        #     self.template_name = "v2/secure/log-events.html"
        # else:
        #     self.template_name = "v2/secure/list-logs.html"
        #     logs = (
        #         AnswerEvent.get_queryset(
        #             user=self.request.user,
        #             exam__chapter__code=chapter_code,
        #             valid=False,
        #         )
        #         .select_related("exam")
        #         .values_list(
        #             "exam__slug",
        #             "exam__name",
        #             "exam__chapter__name",
        #             "exam__question_code",
        #             "exam__question_category__name",
        #         )
        #         .order_by("exam__question_code")
        #         .distinct()
        #     )

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class AnsweredTableView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    @check_profile
    @check_subscription
    def post(self, *args, **kwargs):
        form = V2ExamTableForm(
            data=self.request.POST,
            initial=dict(chapter_code=kwargs.get("chapter_code")),
        )
        data = dict(data=list())
        if form.is_valid():
            data["status"] = "SUCCESS"
            data["data"] = form.cleaned_data.pop("table")
            data["s_data"] = {"upon": form.cleaned_data.pop("upon")}
            header_cnt = form.cleaned_data.pop("header_cnt", None)
            if header_cnt:
                data["s_data"]["header_cnt"] = header_cnt
        else:
            data["status"] = "FAILURE"
            data["error"] = form.errors

        return render_api_response(**data)


class AnsweredView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    @check_profile
    @check_subscription
    def post(self, *args, **kwargs):
        q_slug = kwargs.get("q_slug").__str__()
        data = list()
        if self.request.POST.get("reset"):
            ExamAnswer.get_queryset(
                exam__slug=q_slug, user=self.request.user
            ).delete()
            AnswerEvent.get_queryset(
                user=self.request.user, exam__slug=q_slug, archive=None
            ).update(archive=id_generator(6))
            return render_api_response(data)

        answers = (
            ExamAnswer.get_queryset(exam__slug=q_slug, user=self.request.user)
            .select_related(
                "qun", "tbl_name", "tbl_header", "attribute", "rule"
            )
            .order_by("rule__pair_attr__code", "rule__pair_attr_priority")
        )

        for row in answers:
            if not row.tbl_name:
                continue

            if row.rule:
                pair = row.rule.pair_attr
                if pair:
                    pair = pair.code

                data.append(
                    dict(
                        slug=row.qun.slug.__str__(),
                        action=[
                            f"{row.tbl_name.code}#{row.tbl_header.code}#"
                            f"{row.operation_name}"
                        ],
                        amount=row.amount,
                        tbl_name=row.tbl_name.name,
                        pair=pair,
                        order=row.rule.pair_attr_priority,
                    )
                )

        return render_api_response(data)


class AnswerHistoryView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    @check_profile
    @check_subscription
    def post(self, *args, **kwargs):
        q_slug = kwargs.get("q_slug").__str__()
        events = AnswerEvent.get_queryset(
            exam__slug=q_slug, user=self.request.user, archive=None
        )
        return render_api_response(
            list(
                events.values(
                    "c_on",
                    "user_answer",
                    "valid",
                    "score",
                    "answer_by",
                    "hint",
                    element=F("qun__attribute__name"),
                )
            )
        )


class AnswerStep1View(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    @check_profile
    @check_subscription
    def post(self, *args, **kwargs):
        ans_form = V2AnswerFrom(
            self.request.POST, initial={"request": self.request}
        )
        if ans_form.is_valid():
            return render_api_response(
                ans_form.cleaned_data, status="SUCCESS", code="ANS01"
            )
        else:
            return render_api_response(
                ans_form.errors, status="FAILURE", code="ANS02"
            )


class AnswerView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v3/secure/%s/answer.html"

    @check_profile
    @check_subscription
    def get(self, request, *args, **kwargs):
        q_slug = kwargs.get("q_slug")
        chapter_code = kwargs.get("chapter_code")
        self.template_name = self.template_name % (chapter_code,)

        question = None

        if q_slug:
            # ToDO: validate slug with chapter code.
            question = Exam.get_slug_by_exam(q_slug)
            if not question:
                return render(
                    request,
                    self.template_name,
                    context=locals(),
                    content_type="text/html",
                )

            debit_balance = question.get_debit_balance

            ans = ExamAnswer.get_queryset(
                user=request.user, exam=question
            ).order_by("c_on")

        if chapter_code in (
                "ch4",
                "ch6",
                "ch7",
        ):
            debit_balance = question.get_ch4_transaction

        elif chapter_code in (
                "ch3",
                "ch5",
        ):
            debit_balance = question.get_ch3_transaction

        elif chapter_code in (
                "ch1",
                "ch2",
        ):
            credit_balance = question.get_credit_balance

            adjustment = question.get_adjustment

            table_name = [
                "trading account",
                "profit & loss account",
                "balance sheet",
            ]
            tables = [
                {
                    "title": "trading account",
                    "code": "tr",
                    "header1": ["dr", "cr"],
                    "header2": ["particulars", "particulars"],
                    "fixed_particular": {
                        "dr": [
                            {
                                "txt": "to gross profit",
                                "cls": "profit",
                                "pair": "tr-dr-p-1",
                            }
                        ],
                        "cr": [
                            {
                                "txt": "by gross loss",
                                "cls": "loss",
                                "pair": "tr-cr-l-2",
                            }
                        ],
                    },
                },
                {
                    "title": "profit & loss account",
                    "code": "pl",
                    "header1": ["dr", "cr"],
                    "header2": ["particulars", "particulars"],
                    "fixed_particular": {
                        "dr": [
                            {
                                "txt": "to gross loss",
                                "cls": "loss",
                                "pair": "tr-cr-l-2",
                            },
                            {
                                "txt": "to net profit",
                                "cls": "profit",
                                "pair": "pl-dr-p-1",
                            },
                        ],
                        "cr": [
                            {
                                "txt": "by gross profit",
                                "cls": "profit",
                                "pair": "tr-dr-p-1",
                            },
                            {
                                "txt": "by net loss",
                                "cls": "loss",
                                "pair": "pl-cr-l-2",
                            },
                        ],
                    },
                },
                {
                    "title": "balance sheet",
                    "code": "bs",
                    "header1": ["ls", "as"],
                    "header2": ["liabilities", "assets"],
                    "fixed_particular": {
                        "ls": [
                            {
                                "txt": "add:net profit",
                                "cls": "profit",
                                "pair": "pl-dr-p-1",
                            },
                            {
                                "txt": "less: net loss",
                                "cls": "loss",
                                "pair": "pl-cr-l-2",
                            },
                        ],
                        "as": [],
                    },
                },
            ]

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )

    @check_profile
    @check_subscription
    def post(self, *args, **kwargs):
        ans_form = V2AnswerFrom(
            self.request.POST, initial={"request": self.request}
        )
        if ans_form.is_valid():
            return render_api_response(
                ans_form.cleaned_data, status="SUCCESS", code="ANS01"
            )
        else:
            return render_api_response(
                ans_form.errors, status="FAILURE", code="ANS02"
            )


class QuestionCreateView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v2/secure/%s/create-question.html"

    def get(self, request, *args, **kwargs):
        chapter_code = kwargs.get("chapter_code")

        ch = dict(
            ch1=QuestionForm,
            ch2=QuestionForm,
            ch3=QuestionCh3Form,
            ch4=QuestionCh4Form,
            ch5=QuestionCh5Form,
            ch6=QuestionCh6Form,
            ch7=QuestionCh7Form,
        )

        form = ch.get(chapter_code)
        # nothing exists, use default ch1 template or return 404 page
        if not form:
            chapter_code = "ch1"
        else:
            form = form(initial={"chapter_code": chapter_code})

        self.template_name = self.template_name % (chapter_code,)

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )

    def post(self, *args, **kwargs):
        chapter_code = kwargs.get("chapter_code")
        name = self.request.POST.get("name")
        self.template_name = self.template_name % (chapter_code,)

        chapter = Chapter.get_queryset(code=chapter_code).first()
        if not chapter:
            return render(
                self.request,
                self.template_name,
                context=locals(),
                content_type="text/html",
            )

        # 1. create exam
        exam_obj = {
            "name": name,
            "is_active": True,
            "chapter": chapter,
            "question_code": self.request.POST.get("question_code"),
            "question_category_id": self.request.POST.get("question_category"),
        }
        ex = Exam(**exam_obj)
        ex1 = ex.save()

        if chapter_code in (
                "ch3",
                "ch4",
                "ch5",
                "ch6",
                "ch7",
        ):
            # journal / academic practices particulars
            sel_journal_balance = self.request.POST.getlist(
                "sel_journal_balance"
            )
            txt_balance1 = self.request.POST.getlist("txt_balance1")
            txt_balance2 = self.request.POST.getlist("txt_balance2")

            # ch7 date, jf
            tr_date_s = self.request.POST.getlist("tr_date")
            ext_jf_lf_s = self.request.POST.getlist("ext_jf_lf")

            transaction_header = TableHeader.get_queryset(name="transaction")
            if transaction_header.exists():
                transaction_header = transaction_header.first()
            else:
                d_obj = {"name": "transaction", "is_active": True}
                transaction_header = TableHeader(**d_obj).save()

            for index, jr in enumerate(sel_journal_balance):
                if not jr:
                    continue
                jr_obj = {
                    "exam": ex,
                    "tbl_header": transaction_header,
                    "attribute_id": jr,
                    "amount": 0
                    if not txt_balance1[index]
                    else txt_balance1[index],
                    "amount2": 0
                    if not txt_balance2[index]
                    else txt_balance2[index],
                }

                if chapter_code == "ch7":
                    jr_obj["tr_date"] = tr_date_s[index]
                    jr_obj["ext_jf_lf"] = ext_jf_lf_s[index]

                d1 = ExamQuestion(**jr_obj)
                d1.save()

            form = QuestionCh3Form(initial={"chapter_code": chapter_code})
            if chapter_code == "ch4":
                form = QuestionCh4Form(initial={"chapter_code": chapter_code})
            elif chapter_code == "ch7":
                form = QuestionCh7Form(initial={"chapter_code": chapter_code})

        elif chapter_code in (
                "ch1",
                "ch2",
        ):

            # debit particulars
            sel_debit_balance = self.request.POST.getlist("sel_debit_balance")
            txt_debit_balance = self.request.POST.getlist("txt_debit_balance")
            # credit particulars
            sel_credit_balance = self.request.POST.getlist(
                "sel_credit_balance"
            )
            txt_credit_balance = self.request.POST.getlist(
                "txt_credit_balance"
            )
            # adjustments
            sel_adjustment = self.request.POST.getlist("sel_adjustment")
            txt_adjustment_balance = self.request.POST.getlist(
                "txt_adjustment_balance"
            )

            """
            2. insert debit and credit attributes and amount
            trading account
            """

            debit_header = TableHeader.get_queryset(name="debit particulars")
            if debit_header.exists():
                debit_header = debit_header.first()
            else:
                d_obj = {"name": "debit particulars", "is_active": True}
                debit_header = TableHeader(**d_obj).save()

            credit_header = TableHeader.get_queryset(name="credit particulars")
            if credit_header.exists():
                credit_header = credit_header.first()
            else:
                c_obj = {"name": "credit particulars", "is_active": True}
                credit_header = TableHeader(**c_obj).save()

            adj_header = TableHeader.get_queryset(name="adjustments")
            if adj_header.exists():
                adj_header = adj_header.first()
            else:
                c_obj = {"name": "adjustments", "is_active": True}
                credit_header = TableHeader(**c_obj).save()

            for index, debit in enumerate(sel_debit_balance):
                if not debit:
                    continue
                debt_obj = {
                    "exam": ex,
                    "tbl_header": debit_header,
                    "attribute_id": debit,
                    "amount": txt_debit_balance[index],
                }

                d1 = ExamQuestion(**debt_obj)
                d1.save()

            for index, credit in enumerate(sel_credit_balance):
                if not credit:
                    continue
                credit_obj = {
                    "exam": ex,
                    "tbl_header": credit_header,
                    "attribute_id": credit,
                    "amount": txt_credit_balance[index],
                }

                c1 = ExamQuestion(**credit_obj)
                c1.save()

            for index, adj in enumerate(sel_adjustment):
                if not adj:
                    continue
                adj_obj = {
                    "exam": ex,
                    "tbl_header": adj_header,
                    "attribute_id": adj,
                    "amount": txt_adjustment_balance[index],
                }

                a1 = ExamQuestion(**adj_obj)
                a1.save()

            form = QuestionForm(initial={"chapter_code": chapter_code})

        success = "Question saved successfully."

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class ChapterQuestionCreateView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = True
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v2/secure/chapter-question-create.html"
    tabs = None

    def get(self, request, *args, **kwargs):
        chapters = Chapter.get_queryset(is_active=1).order_by("code")

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class QuestionView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v2/secure/list-question.html"
    tabs = None

    @check_profile
    @check_subscription
    def get(self, request, *args, **kwargs):
        chapter_code = kwargs.get("chapter_code")
        q_slug = kwargs.get("q_slug").__str__()

        questions = Exam.get_queryset(
            chapter__code=chapter_code, is_active=True
        ).select_related("chapter")

        if q_slug:
            question = questions.filter(slug=q_slug)
            question = question.first()

            # if question slug not exists in subscription, redirect to
            # subscription page
            if self.request.user.is_trail:
                questions1 = questions.filter(
                    question_category=question.question_category
                )
                questions1 = questions1[:2]
                slg = questions1.values_list("slug", flat=True)
                slg_dict = {s: True for s in slg}
                if not slg_dict.get(q_slug):
                    return redirect("website_v2:course-subscribe-1")

            self.template_name = "v2/secure/%s/question-details.html" % (
                chapter_code,
            )

            if chapter_code in (
                    "ch4",
                    "ch6",
                    "ch7",
            ):
                debit_balance = question.get_ch4_transaction
            elif chapter_code in (
                    "ch3",
                    "ch5",
            ):
                debit_balance = question.get_ch3_transaction
            else:
                debit_balance = question.get_debit_balance
                credit_balance = question.get_credit_balance

                adjustment = question.get_adjustment

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class ChapterView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v2/secure/chapter.html"
    tabs = None

    @check_profile
    @check_permission
    def get(self, request, *args, **kwargs):

        chapter_code = kwargs.get("chapter_code")
        qun_category = kwargs.get("qun_category")

        if not chapter_code:
            chapters = Chapter.get_queryset(is_active=1).order_by("code")
            self.template_name = "v2/secure/chapter.html"

        elif chapter_code and not qun_category:
            qun_category = QuestionCategory.get_queryset(is_active=1)
            try:
                chapter_name = Chapter.get_queryset(
                    code=chapter_code).first().name
            except Exception:
                chapter_name = ""
            self.template_name = "v2/secure/chapter-category.html"

        elif chapter_code and qun_category:
            self.template_name = "v2/secure/list-question.html"
            try:
                chapter_name = Chapter.get_queryset(
                    code=chapter_code).first().name
                cat_name = QuestionCategory.get_queryset(
                    code=qun_category).first().name
            except Exception:
                chapter_name = ""
                cat_name = ""

            questions = Exam.get_queryset(
                chapter__code=chapter_code,
                question_category__code=qun_category,
            ).select_related("chapter", "question_category")

            if not self.request.user.is_superuser:
                questions = questions.filter(is_active=True)

            if self.request.user.is_trail:
                questions = questions[:2]

            # count
            # q = questions.values("question_category__code").annotate(
            # total=Count("question_category__id"))
            # print(q)

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class HomeView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "secure/home.html"
    tabs = None

    @check_profile
    @check_subscription
    def get(self, request, *args, **kwargs):
        # recently added top 5 question
        recent = Exam.get_recent_exam()
        # most answered top 5 question
        most_answered = ExamAnswer.get_most_answered_exam()
        # self attempted 5 question
        most_attempted = ExamAnswer.get_last_answered_exam(request.user)

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class SiChapterView(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = False
    login_url = "/login/?i=hm"

    permission_checker = None

    template_name = "v3/secure/sr-inter.html"
    tabs = None

    @check_profile
    @check_subscription
    def get(self, request, *args, **kwargs):
        chapter_code = kwargs.get("chapter_code")
        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class BackupRuleEngine(LoginRequiredMixin, View):
    requires_login = True
    requires_superuser = True
    login_url = "/login/?i=hm"

    template_name = "secure/home.html"

    def get(self, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.
        rules = (
            RuleEngine.get_queryset()
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
            .all()
        )

        header = None
        res_data = list()

        if rules.exists():
            for row in rules:
                data_dict = dict()
                data_dict["field_name"] = row.attribute_name
                data_dict["field_type"] = row.tbl_attribute_type.name
                data_dict["chapter"] = row.chapter

                data_dict["pair_attr"] = row.pair_attr
                data_dict["pair_attr_priority"] = row.pair_attr_priority

                data_dict["relationship"] = row.rel_name

                data_dict["arithmetic1"] = row.operation1
                data_dict["table1_name"] = row.tbl1
                data_dict["header1_name"] = row.header1
                data_dict["information1"] = row.help1

                data_dict["arithmetic2"] = row.operation2
                data_dict["table2_name"] = row.tbl2
                data_dict["header2_name"] = row.header2
                data_dict["information2"] = row.help2

                data_dict["arithmetic3"] = row.operation3
                data_dict["table3_name"] = row.tbl3
                data_dict["header3_name"] = row.header3
                data_dict["information3"] = row.help3

                res_data.append(data_dict)

                if not header:
                    header = list(data_dict.keys())

        return streaming_zip_view(header, res_data)
