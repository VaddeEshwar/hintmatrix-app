from datetime import timedelta
from string import ascii_uppercase

from django.apps import apps
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now

from utils.generate_key import code_generator, id_generator
from utils.models import AbstractModel


class CollageDetails(AbstractModel):
    """
    record college details.
    """

    admin_user = models.OneToOneField(
        "auth.User", on_delete=models.SET_NULL, null=True
    )
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=64)
    email = models.EmailField(null=True)
    contact_no = models.CharField(
        max_length=10, null=True, verbose_name="Contact Number"
    )
    # whatsapp number
    wa_number = models.CharField(
        max_length=16, null=True, verbose_name="Whatsapp Mobile No"
    )
    address = models.CharField(
        max_length=512, null=True, verbose_name="address"
    )
    state = models.ForeignKey(
        "config.State",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="state",
    )


class CollegeWiseUser(AbstractModel):
    """
    record college wise users
    """

    college = models.ForeignKey(
        CollageDetails, on_delete=models.SET_NULL, null=True
    )
    username = models.CharField(max_length=256)
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)


class UserWiseReference(AbstractModel):
    """
    user invited by
    """

    referral_code = models.CharField(max_length=16)
    username = models.CharField(max_length=256)
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    user_agent = models.CharField(max_length=512, default="n/a")
    ip_address = models.GenericIPAddressField(
        default="a00f:a000:a000:a000:0000:a000:a000:a000"
    )
    # if user subscribed with any package
    # null, not yet. True, Subscribed. False, invalid
    is_subscribed = models.BooleanField(null=True, default=None)
    # user purchase amount
    subscription_amount = models.FloatField(null=True, default=None)
    # for this transaction eligible referral amount.
    referral_amount = models.FloatField(null=True, default=None)
    # null, not yet. True, paid. False, invalid
    is_paid = models.BooleanField(null=True, default=None)
    # amount paid on
    paid_on = models.DateField(null=True, default=None)

    @classmethod
    def get_or_create_record(cls, **kwargs):
        """
        The get_or_create_record function is a class method that takes in
        keyword arguments and returns an object.
        It will either get the existing record or create a new one if it
        doesn't exist.

        :param cls: Pass in the class name of the model
        :param **kwargs: Pass a variable number of keyword arguments to
        the function
        :return: A tuple of the form (object, created), where object is the
        retrieved or created object and created is a boolean specifying
        whether a new object was created
        :doc-author: Trelent/Naresh
        """
        return cls.objects.get_or_create(**kwargs)


class UserReferenceCode(AbstractModel):
    """
    user invitation details
    """

    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    referral_code = models.CharField(max_length=16, unique=True)

    @classmethod
    def create_new_referral_code(cls, user, code=None):
        """
        The create_new_referral_code function creates a new referral code
        for the user.
            If no code is provided, it generates one and checks to make sure
            that it doesn't already exist in the database.
            It then returns a row with the newly created referral code.

        :param cls: Refer to the class itself
        :param user: Get the user object
        :param code: Generate a code that is used to refer the user
        :return: A row
        :doc-author: Trelent/Naresh
        """
        if not code:
            # generate code
            code = id_generator(6, chars=ascii_uppercase)
            while cls.get_queryset(referral_code=code).exists():
                code = id_generator(6, chars=ascii_uppercase)

        row, _ = cls.get_queryset().get_or_create(
            user=user, referral_code=code, is_active=1, status=1
        )
        return row


class SubscriptionPermission(AbstractModel):
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    purchase_order = models.ForeignKey(
        "shop.PurchaseOrder", on_delete=models.SET_NULL, null=True
    )
    product = models.ForeignKey(
        "shop.Product", on_delete=models.SET_NULL, null=True
    )
    valid_to = models.DateField()

    def is_expired(self):
        """
        The is_expired function checks if the valid_to date is less than
        tomorrow's date.
        If it is, then the function returns True. Otherwise, it returns False.

        :param self: Represent the instance of the class
        :return: True if the valid_to date is less than tomorrow's date
        :doc-author: Trelent/Naresh
        """
        if self.valid_to < (now().date() + timedelta(days=1)):
            return True
        return False

    @classmethod
    def create_order(cls, user, purchase_order, product, trail=False):
        # update calling again with same parameters
        """
        The create_order function creates a new order for the user.


        :param cls: Create the object
        :param user: Identify the user who is purchasing the product
        :param purchase_order: Create a purchase order for the user
        :param product: Determine the number of days that the subscription
        will last
        :param trail: Determine whether the subscription is a trial or not
        :return: A service-purchase object
        :doc-author: Trelent/Naresh
        """
        sp_dict = {
            "user": user,
            "purchase_order": purchase_order,
            "product": product,
            "valid_to": (now().date() + timedelta(days=7)),
        }
        if not trail:
            sp_dict["valid_to"] = now().date() + timedelta(days=product.days)
            sp = cls(**sp_dict)
            sp.save()
        else:
            # one time trail service for 7 days.
            sp = cls.get_queryset(user=user, product=product)
            if not sp.exists():
                sp = cls(**sp_dict)
                sp.save()
            else:
                sp = sp.first()

        return sp

    @classmethod
    def has_permission(cls, user, chapter_code, course_code=None):
        """
        The has_permission function is a class method that takes in the
        user, chapter_code and course_code.
        It returns a queryset of all the valid subscriptions for that user
        with the given chapter code and course code.
        The function also checks if there are any subscriptions with no
        chapters or courses associated to it.

        :param cls: Pass the class object to the function
        :param user: Filter the queryset to only include permissions
        :param chapter_code: Filter the queryset by chapter_code
        :param course_code: Filter the queryset by course code
        :return: A queryset, which is a list of objects
        :doc-author: Trelent
        """
        course_code = "fy" if not course_code else course_code
        _yesterday = now().date() + timedelta(days=-1)
        _has = (
            cls.get_queryset(
                user=user,
                valid_to__gt=_yesterday,
                product__course__code=course_code,
            )
            .filter(
                models.Q(product__chapter__code=None) | models.Q(
                    product__chapter__code=chapter_code)
            )
            .select_related("product", "product__course", "product__chapter")
        )
        # print(_has.query)
        return _has


class Invoice(AbstractModel):
    user = models.OneToOneField(
        "auth.User", on_delete=models.SET_NULL, null=True
    )
    inv_no = models.CharField(max_length=8, default=code_generator)

    customer_address = models.CharField(
        max_length=512, null=True, verbose_name="address"
    )
    customer_state = models.ForeignKey(
        "config.State",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="state",
    )

    taxable_amount = models.FloatField(default=0)
    cgst = models.FloatField(default=0)
    sgst = models.FloatField(default=0)
    igst = models.FloatField(default=0)
    total_tax = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)


class InvoiceItem(AbstractModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        "shop.Product", on_delete=models.SET_NULL, null=True
    )
    quantity = models.SmallIntegerField(default=0)
    taxable_amount = models.FloatField(default=0)
    gst = models.FloatField(default=0)
    total_tax = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)


class Profile(AbstractModel):
    user = models.OneToOneField(
        "auth.User", on_delete=models.SET_NULL, null=True
    )
    mobile = models.CharField(
        max_length=10, null=True, verbose_name="Mobile Number"
    )
    # whatsapp number
    is_wa_number = models.BooleanField(
        default=False, verbose_name="Whatsapp Notification"
    )
    address = models.CharField(
        max_length=512, null=True, verbose_name="address"
    )
    state = models.ForeignKey(
        "config.State",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="state",
    )

    @cached_property
    def total_user_marks(self):
        """
        It returns the sum of the scores of all the answers submitted by
        the user
        :return: The total marks of the user.
        """
        answer_event_model = apps.get_model(
            app_label="answer", model_name="AnswerEvent"
        )
        return answer_event_model.total_marks(user=self.user)

    @cached_property
    def chapter_wise_user_marks(self):
        """
        The chapter_wise_user_marks function returns a dictionary of the
        user's marks for each chapter in the course.
        The keys are chapter names, and the values are dictionaries with
        keys 'total_marks' and 'obtained_marks'.

        :param self: Refer to the instance of the class
        :return: A dictionary of chapter wise marks
        :doc-author: Trelent
        """
        answer_event_model = apps.get_model(
            app_label="answer", model_name="AnswerEvent"
        )
        course_wise = answer_event_model.chapter_wise_marks(user=self.user)
        return course_wise

    @cached_property
    def get_reference_code(self):
        """
        The get_reference_code function is used to get the referral
        code of a user.
        If the user does not have an active referral code, it creates one
        for them and returns it.
        Otherwise, it returns their existing active referral code.

        :param self: Represent the instance of the class
        :return: A userreferencecode object
        :doc-author: Trelent
        """
        r_code = UserReferenceCode.get_queryset(user=self.user, is_active=1)
        if not r_code.exists():
            return UserReferenceCode.create_new_referral_code(user=self.user)

        return r_code.first()

    @cached_property
    def reference_data(self):
        """
        The reference_data function returns a list of dictionaries containing
        the username, first name, subscription amount, referral amount and
        whether or not the user has been paid. The function is
        limited to 25 users.

        :param self: Represent the instance of the class
        :return: A list of dictionaries
        :doc-author: Trelent
        """
        return (
            UserWiseReference.get_queryset(
                referral_code=self.get_reference_code.referral_code
            )
            .exclude(user=None)
            .values(
                "username",
                "user__first_name",
                "subscription_amount",
                "referral_amount",
                "is_paid",
            )[:25]
        )
