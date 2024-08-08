import json
from uuid import UUID

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from utils.models import AbstractModel


class Product(AbstractModel):
    course = models.ForeignKey(
        "config.Course", on_delete=models.SET_NULL, null=True)
    chapter = models.ForeignKey(
        "config.Chapter", on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    price = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
        ],
    )
    days = models.PositiveIntegerField(default=0)
    reward = models.PositiveIntegerField(
        default=0,
        help_text="amount of reward",
        validators=[
            MinValueValidator(0),
        ],
    )
    gst = models.FloatField(default=0)

    class Meta:
        ordering = ("-days", "code")

    def __str__(self):
        return self.name


class ProductWiseChapter(AbstractModel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    chapter = models.ForeignKey(
        "config.Chapter", on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=8)

    class Meta:
        ordering = ("c_on", "code")

    def __str__(self):
        return self.chapter.name


class PurchaseOrder(AbstractModel):
    # order id, as slug of the record.
    # code = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=256)
    total_cost = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
        ],
    )
    note = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def calculate_total(self):
        total = OrderDetails.get_queryset(
            purchase_order=self).aggregate(Sum("price"))
        # print(32, total)
        return total.get("price__sum", 0.0)

    @classmethod
    def create_order(cls, request, user, product):
        if product.price < 1:
            od = OrderDetails.get_queryset(
                purchase_order__user=request.user, product=product
            ).select_related("purchase_order", "product")

            if od.exists():
                return od.first().purchase_order, od

        po = cls(
            **{
                "user": user,
                "name": f"Payment for [{product.name}].",
                "total_cost": product.price,
                "note": request.META.get("REMOTE_ADDR", "n/a"),
            }
        )
        po.save()

        od = OrderDetails(
            **{
                "purchase_order": po,
                "product": product,
                "quantity": 1,
                "price": product.price,
                "user_agent": request.META.get("HTTP_USER_AGENT"),
                "ip_address": request.META.get("REMOTE_ADDR", "0.0.0.0")
            }
        )
        od.save()
        return po, [od]


class OrderDetails(AbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.SET_NULL, null=True
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
        ],
    )
    user_agent = models.CharField(
        max_length=512, null=True, blank=True)
    ip_address = models.CharField(
        max_length=64, null=True, blank=True)


class PgNotify(AbstractModel):
    pg_name = models.CharField(max_length=64, null=True)
    order_id = models.UUIDField(null=True)
    response = models.TextField(null=True)
    request_obj = models.TextField(null=True)

    @classmethod
    def create_notify(cls, pg_response, request_obj, pg_name="cf"):
        # try:
        #     pg_response = pg_response.decode("utf-8")
        #     pg_response = json.loads(pg_response)
        # except Exception as e:
        #     pg_response = {
        #         "error": e.__str__(),
        #         "data": pg_response
        #     }
        #
        # order_id = pg_response.get("data", {}).get("order", {}).get(
        #     "order_id")
        # if not order_id:
        data = pg_response.get("data", {})
        order_id = data.get("link_id")

        try:
            uuid_obj = UUID(order_id, version=4).__str__()
        except Exception:
            uuid_obj = "11111111-1111-1111-1111-111111111111"

        pn = dict(
            pg_name=pg_name,
            order_id=uuid_obj,
            response=json.dumps(pg_response),
            request_obj=json.dumps(request_obj.__dict__.__str__()),
        )
        p = cls(**pn)
        p.save()
        return p


class PgReturn(AbstractModel):
    order_id = models.UUIDField()
    token = models.CharField(max_length=255)
    response = models.TextField(null=True)
    request_obj = models.TextField(null=True)

    @classmethod
    def create_return(cls, order_id, token, pg_response, request_obj):
        pr = dict(
            order_id=order_id,
            token=token,
            response=pg_response,
            request_obj=request_obj.__dict__.__str__(),
        )
        p = cls(**pr)
        p.save()
        return p
