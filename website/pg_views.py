import json
import logging

from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from account.models import SubscriptionPermission, UserWiseReference
from shop.models import OrderDetails, PgNotify, PgReturn
from utils.cash_free_pg import pg_order_details

logger = logging.getLogger(__name__)


class PgReturnViewV2(View):
    def get(self, *args, **kwargs):
        # print(17, self)
        return redirect("website_v2:my-course")

    def post(self, *args, **kwargs):
        # print(21, self)
        return redirect("website_v2:my-course")


@method_decorator(csrf_exempt, name="dispatch")
class PgNotifyView(View):
    def post(self, *args, **kwargs):
        pg_name = kwargs.get("pg_name", "cf")

        order_id = None

        if "form" in self.request.content_type:
            payload = self.request.POST.dict().copy()
            payload["form"] = True
            try:
                payload["order_id"] = self.request.POST.get("orderId")
                payload["tx_status"] = self.request.POST.get("txStatus")
            except Exception as e:
                payload = {"error": e.__str__(), "data": payload}

            p = PgNotify.create_notify(
                pg_response=payload, request_obj=self.request, pg_name=pg_name
            )
            return JsonResponse(
                dict(
                    referenceId=payload.get("referenceId"),
                    msg=p.id
                )
            )

        else:
            payload = self.request.body
            try:
                payload = payload.decode("utf")
                payload = json.loads(payload)
                payload["body"] = True
                # order_id = (
                #     payload.get("data", {}).get("order", {}).get("order_id")
                # )
                order_id = payload.get("data", {})["link_id"]
                payload["order_id"] = order_id
                payload["tx_status"] = (
                    payload.get("data", {})
                    .get("order", {})
                    .get("payment_status")
                )
            except Exception as e:
                payload = {"error": e.__str__(), "data": payload, "lno":70}

        try:
            p = PgNotify.create_notify(
                pg_response=payload, request_obj=self.request, pg_name=pg_name
            )

            try:
                link_status = payload.get("data")["link_status"]
                link_status = link_status.lower()
                if link_status == "paid":
                    set_product_permission(
                        order_id=order_id,
                        user_agent=self.request.META.get(
                            "HTTP_USER_AGENT"
                        ),
                        ip_address=self.request.META.get(
                            "REMOTE_ADDR"
                        ),
                        referral_email=payload.get(
                            "customer_details", {}
                        ).get("customer_email", ""))

            except Exception as e1:
                return JsonResponse({"msg": e1.__str__(), "lno":94})

            return JsonResponse({"msg": p.id})
        except Exception as e:
            return JsonResponse({"msg": e.__str__(), "lno": 98})

    def get(self, *args, **kwargs):
        return self.post(args, kwargs)


class PgReturnView(View):
    def get(self, *args, **kwargs):
        order_id = kwargs.get("order_id")
        req_status, order_details = pg_order_details(order_id)
        order_token = kwargs.get("order_token")
        # print(req_status, order_details)

        if req_status == 200 and (
                order_details.get("order_token") == order_token
        ):
            order_status = order_details.get("order_status", "").lower()
            order_id = order_details.get("order_id", "")
            if order_status == "paid":
                # create permission
                # save pg order details
                PgReturn.create_return(
                    order_id=order_id,
                    token=order_token,
                    pg_response=order_details,
                    request_obj=self.request,
                )

                po = OrderDetails.get_queryset(
                    purchase_order__slug=order_id
                ).first()

                SubscriptionPermission.create_order(
                    po.purchase_order.user,
                    purchase_order=po.purchase_order,
                    product=po.product,
                )
                # Commission will be paid  for all subscriptions done
                # within 30days from the date of signup.
                user = po.purchase_order.user
                if (now().date() - user.date_joined.date()).days < 31:
                    customer_email = order_details.get(
                        "customer_details", {}
                    ).get("customer_email", "")
                    if customer_email:
                        ur = UserWiseReference.get_queryset(
                            username=customer_email
                        )
                        if ur.exists():
                            ur_ref = ur.first()
                            if not ur_ref.subscription_amount:
                                ur_ref.is_subscribed = True
                                ur_ref.subscription_amount = po.product.price
                                ur_ref.referral_amount = po.product.reward
                                ur_ref.paid_on = now().date()
                                ur_ref.save()
                            else:
                                (
                                    row,
                                    _,
                                ) = UserWiseReference.get_or_create_record(
                                    referral_code=ur_ref.referral_code,
                                    username=customer_email,
                                    user=user,
                                    is_active=1,
                                    user_agent=self.request.META.get(
                                        "HTTP_USER_AGENT"
                                    ),
                                    ip_address=self.request.META.get(
                                        "REMOTE_ADDR"
                                    ),
                                    is_subscribed=True,
                                    subscription_amount=po.product.price,
                                    referral_amount=po.product.reward,
                                    paid_on=now().date(),
                                )

                # if referral found in the same session, set rewards for the
                # same.
                # referral_id = self.request.session.get("referral_row_id")
                # if referral_id:
                #     ur_ref = UserWiseReference.get_queryset(
                #         id=referral_id
                #     ).first()
                #     if ur_ref:
                #         """
                #         Get purchase amount and product as well rewards.
                #         update reference with amount and commission based on
                #         product.
                #         """
                #         ur_ref.is_subscribed = True
                #         ur_ref.subscription_amount = po.product.price
                #         ur_ref.referral_amount = po.product.reward
                #         ur_ref.paid_on = now().date()
                #         ur_ref.save()

        return redirect("website_v2:my-course")


def set_product_permission(order_id, user_agent, ip_address, referral_email):
    po = OrderDetails.get_queryset(
        purchase_order__slug=order_id
    ).first()

    sp = SubscriptionPermission.create_order(
        po.purchase_order.user,
        purchase_order=po.purchase_order,
        product=po.product,
    )
    logger.info(f" user's {po.purchase_order.user} permission set {sp.id}")
    # Commission will be paid  for all subscriptions done
    # within 30days from the date of signup.
    user = po.purchase_order.user
    if referral_email and (now().date() - user.date_joined.date()).days < 31:
        customer_email = referral_email
        if customer_email:
            ur = UserWiseReference.get_queryset(
                username=customer_email
            )
            if ur.exists():
                ur_ref = ur.first()
                if not ur_ref.subscription_amount:
                    ur_ref.is_subscribed = True
                    ur_ref.subscription_amount = po.product.price
                    ur_ref.referral_amount = po.product.reward
                    ur_ref.paid_on = now().date()
                    ur_ref.save()
                else:
                    (
                        row,
                        _,
                    ) = UserWiseReference.get_or_create_record(
                        referral_code=ur_ref.referral_code,
                        username=customer_email,
                        user=user,
                        is_active=1,
                        user_agent=user_agent,
                        ip_address=ip_address,
                        is_subscribed=True,
                        subscription_amount=po.product.price,
                        referral_amount=po.product.reward,
                        paid_on=now().date(),
                    )
