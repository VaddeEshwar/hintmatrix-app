import logging
from functools import wraps

from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import generic
from django.views.generic import FormView
from django.views.generic.base import View

from account.models import Profile as UserProfile
from account.models import UserWiseReference
from question.models import Exam
from website.forms import ForgotEmailForm, PasswordResetRequestForm

logger = logging.getLogger("django")


def check_save_referral(view_func):
    """
    saves user email with referral code.
    """

    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        if request.method != "POST":
            if request.session.get("signup"):
                del request.session["signup"]
            return view_func(request, *args, **kwargs)

        if request.method == "POST":
            request.session["signup"] = request.POST.dict().copy()

        referral_code = request.GET.get("ref")
        if not referral_code:
            return view_func(request, *args, **kwargs)

        email = request.POST.get("username")
        if User.objects.filter(username=email).exists():
            return view_func(request, *args, **kwargs)

        try:
            row, _ = UserWiseReference.get_or_create_record(
                referral_code=referral_code,
                username=email,
                is_active=1,
                user_agent=request.META.get("HTTP_USER_AGENT"),
                ip_address=request.META.get("REMOTE_ADDR"),
            )

            # define user referral code in session
            # define username
            # request.session["referral_code"] = referral_code
            # request.session["username"] = email

            # If user takes paid subscription, use this session variable to
            # update userwisereference record is_paid=True,
            # subscription_amount and referral_amount with business validation.
            request.session["referral_row_id"] = row.id

        except Exception as e:
            logger.error(str(e))
            print(65, str(e))

        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


class BlogView(View):
    template_name = "blog.html"
    tabs = None

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class ArticleShipView(View):
    template_name = "articleship.html"
    tabs = None

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class QuestionView(View):
    template_name = "v2/list-question.html"
    tabs = None

    def get(self, request, *args, **kwargs):
        chapter_code = kwargs.get("chapter_code")
        q_slug = kwargs.get("q_slug")
        if q_slug:
            self.template_name = "v2/secure/%s/question-details.html" % (
                chapter_code,
            )
            question = Exam.get_queryset(slug=q_slug).select_related("chapter")
            question = question.first()

            debit_balance = question.get_debit_balance
            credit_balance = question.get_credit_balance

            adjustment = question.get_adjustment

        else:

            questions = Exam.get_queryset(is_active=True).select_related(
                "chapter"
            )

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class IndexView(View):
    permission_checker = None

    template_name = "index1.html"

    def get(self, request):
        # services = ServiceName.objects.filter(is_active=True)

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


@method_decorator(check_save_referral, name="dispatch")
class SignUpView(generic.CreateView):
    # https://learndjango.com/tutorials/django-signup-tutorial
    # import django.contrib.auth.password_validation as validators
    form_class = UserCreationForm
    success_url = reverse_lazy("website_v2:signup-done")
    template_name = "registration/signup.html"
    context_object_name = "signup"


class SignUpDoneView(View):
    template_name = "registration/signup-done.html"

    def get(self, request):
        # to handle reference info
        signup_data = self.request.session.get("signup")
        if signup_data and isinstance(signup_data, dict):
            # username there, create user profile.
            print(signup_data)
            try:
                user = User.objects.get(username=signup_data.get("username"))
                user.first_name = signup_data.get("first_name")
                user.save()

                referral_row_id = request.session.get("referral_row_id")
                if referral_row_id:
                    ref = UserWiseReference.get_queryset(
                        id=referral_row_id
                    ).first()
                    ref.user = user
                    ref.save()

                UserProfile.objects.get_or_create(
                    user=user,
                    mobile=signup_data.get("mobile"),
                    address=signup_data.get("address"),
                    state_id=signup_data.get("state"),
                )

                del self.request.session["signup"]
            except Exception as e:
                print(152, str(e))
                pass

        return render(
            request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class SetForgotPasswordView(View):
    form_class = SetPasswordForm
    template_name = "registration/forgot-password-set.html"

    def get(self, *args, **kwargs):
        """
        Activate user account.
        :param args:
        :param kwargs:
        :return:
        """
        cache_id = kwargs.get("cache_id").__str__()
        user_email = cache.get(cache_id)
        if not user_email:
            return redirect("website_v2:forgot-password")

        form = self.form_class(user=None)

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )

    def post(self, *args, **kwargs):
        """
        Activate user account.
        :param args:
        :param kwargs:
        :return:
        """
        cache_id = kwargs.get("cache_id").__str__()
        user_email = cache.get(cache_id)
        if not user_email:
            return redirect("website_v2:forgot-password")

        else:
            user = User.objects.filter(email=user_email).first()
            form = self.form_class(user, self.request.POST)
            if not form.is_valid():
                errors = form.errors
            else:
                form.save()
                is_reset = True
                cache.delete(cache_id)

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class ForgotPasswordView(View):
    template_name = "registration/forgot-password.html"

    def get(self, *args, **kwargs):
        """
        Activate user account.
        :param args:
        :param kwargs:
        :return:
        """
        form = ForgotEmailForm()
        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )

    def post(self, *args, **kwargs):
        is_email_sent = False
        form = ForgotEmailForm(self.request.POST)
        if form.is_valid():
            is_email_sent = True

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class SignUpActivateView(View):
    template_name = "registration/signup-activate.html"

    def get(self, *args, **kwargs):
        """
        Activate user account.
        :param args:
        :param kwargs:
        :return:
        """
        is_active = False
        cache_id = kwargs.get("cache_id").__str__()
        user_email = cache.get(cache_id)
        if user_email:
            user = User.objects.filter(email=user_email)
            if user.exists():
                user = user.first()
                user.is_active = True
                user.save()

                cache.delete(cache_id)
                is_active = True

        return render(
            self.request,
            self.template_name,
            context=locals(),
            content_type="text/html",
        )


class ResetPasswordRequestView(FormView):
    template_name = "registration/password_reset_email.html"
    success_url = "/forgot-password/"
    form_class = PasswordResetRequestForm

    @staticmethod
    def validate_email_address(email):
        """
        This method here validates the if the input is
        an email address or not.
        Its return type is boolean, True if the input is a
        email address or False
        if its not.
        :param email:
        :return:
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def post(self, request, *args, **kwargs):
        """
        A normal post request which takes input from field "email_or_username"
        (in ResetPasswordRequestForm).
        :param self:
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = self.form_class(request.POST)
        data = None
        if form.is_valid():
            data = form.cleaned_data["email_or_username"]

        if self.validate_email_address(data) is True:
            """
            If the input is an valid email address, then the following
            code will
            lookup for users associated with that email address.
            If found then an
            email will be sent to the address, else an error message
            will be printed on the screen.
            """
            associated_users = User.objects.filter(
                Q(email=data) | Q(username=data)
            )
            if associated_users.exists():
                for user in associated_users:
                    c = {
                        "email": user.email,
                        "domain": request.META["HTTP_HOST"],
                        "site_name": "your site",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    subject_template_name = (
                        "registration/password_reset_subject.txt"
                    )
                    # copied from django/contrib/admin/templates/
                    # registration/password_reset_subject.txt
                    # to templates directory
                    email_template_name = (
                        "registration/password_reset_email.html"
                    )
                    # copied from django/contrib/admin/templates/
                    # registration/password_reset_email.html
                    # to templates directory
                    subject = loader.render_to_string(subject_template_name, c)
                    # Email subject *must not* contain newlines
                    subject = "".join(subject.splitlines())
                    email = loader.render_to_string(email_template_name, c)
                    send_mail(
                        subject,
                        email,
                        DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                result = self.form_valid(form)
                messages.success(
                    request,
                    f"""An email has been sent to {data}.
                    Please check, inbox to continue resetting
                    password.""",
                )
                return result

            result = self.form_invalid(form)
            messages.error(
                request, "No user is associated with this email address"
            )
            return result
        else:
            """
            If the input is an username, then the following code will
            lookup for users associated with that user. If found then
            an email will be sent to the user's address, else an
            error message will be printed on the screen.
            """
            associated_users = User.objects.filter(username=data)
            if associated_users.exists():
                for user in associated_users:
                    c = {
                        "email": user.email,
                        "domain": "example.com",  # or your domain
                        "site_name": "example",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    subject_template_name = (
                        "registration/password_reset_subject.txt"
                    )
                    email_template_name = (
                        "registration/password_reset_email.html"
                    )
                    subject = loader.render_to_string(subject_template_name, c)

                    # Email subject *must not* contain newlines
                    subject = "".join(subject.splitlines())
                    email = loader.render_to_string(email_template_name, c)
                    send_mail(
                        subject,
                        email,
                        DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                result = self.form_valid(form)
                messages.success(
                    request,
                    f"""
                    Email has been sent to {data}'s email address.
                    Please check, inbox to continue resetting password.
                    """,
                )
                return result
            result = self.form_invalid(form)
            messages.error(
                request, "This username does not exist in the system."
            )
            return result
