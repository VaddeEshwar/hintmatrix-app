import pytz
import requests
from django.conf import settings
from django.utils import timezone


def pg_order_details(order_id):
    url = f"{settings.PG_BASE_URL}/{order_id}"
    header = {
        "Content-Type": "application/json",
        "x-api-version": "2022-01-01",
        "x-client-id": settings.PG_APP_ID,
        "x-client-secret": settings.PG_SECRET_KEY,
    }

    res = requests.get(url=url, headers=header)
    return res.status_code, res.json()


def pg_order_create(
    order_id,
    order_amount,
    order_note,
    customer_id,
    customer_email,
    customer_phone,
    payment_for=None
):
    """
    :param order_id:
    :param order_amount:
    :param order_note:
    :param customer_id:
    :param customer_email:
    :param customer_phone:
    :param payment_for:
    :return:
    """
    url = settings.PG_BASE_URL

    header = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "x-api-version": "2022-09-01",
        "x-client-id": settings.PG_APP_ID,
        "x-client-secret": settings.PG_SECRET_KEY,
    }

    data = {
        "order_id": order_id,
        "order_amount": order_amount,
        "order_currency": "INR",
        "order_note": order_note,
        "customer_details": {
            "customer_id": f"{customer_id}",
            "customer_email": customer_email,
            "customer_phone": f"{customer_phone}",
        },
        "order_meta": {
            "return_url": settings.PG_RETURN_URL,
            "notify_url": settings.PG_NOTIFY_URL,
        },
    }

    link_expiry_time = (timezone.datetime.now(
        pytz.timezone('US/Central')) + timezone.timedelta(
        minutes=30)).isoformat()

    payload = {
        "link_amount": order_amount,
        "link_currency": "INR",
        "link_minimum_partial_amount": order_amount,
        "link_id": order_id,
        "link_partial_payments": False,
        "customer_details": {
            "customer_name": f"{customer_id}",
            "customer_phone": f"{customer_phone}",
            "customer_email": customer_email
        },
        "link_expiry_time": link_expiry_time,
        "link_purpose": payment_for,
        "link_notify": {
            "send_sms": False,
            "send_email": True
        },
        "link_auto_reminders": False,
        "link_notes": {
            "key_1": "value_1",
            "key_2": "value_2"
        },
        "link_meta": {
            "notify_url": settings.PG_NOTIFY_URL,
            "return_url": settings.PG_RETURN_URL,
        }
    }

    res = requests.post(url=url, json=payload, headers=header)
    print("PG Object")
    print(res.json())
    return res.json()


#
# """
# {'cf_order_id': 2490827, 'order_id': 'order_1626945143520',
# 'entity': 'order',
# 'order_currency': 'INR', 'order_amount': 10.12,
# 'order_expiry_time': '2022-06-30T12:45:56+05:30',
# 'customer_details': {'customer_id': '12345', 'customer_name': None,
# 'customer_email': 'techsupport@cashfree.com',
# 'customer_phone': '9816512345'},
# 'order_meta': {'return_url': None, 'notify_url': None,
# 'payment_methods': None},
# 'settlements': {
# 'url': 'https://sandbox.cashfree.com/pg/orders/order_1626945143520/
# settlements'
# }, 'payments': {
# 'url': 'https://sandbox.cashfree.com/pg/orders/order_1626945143520/
# payments'},
# 'refunds': {
# 'url': 'https://sandbox.cashfree.com/pg/orders/order_1626945143520/refunds'},
# 'order_status': 'ACTIVE', 'order_token': 'zcTMzGS1V9FyLlYkBPSO',
# 'order_note': 'Additional order info',
# 'payment_link':
# 'https://payments-test.cashfree.com/order/#zcTMzGS1V9FyLlYkBPSO',
# 'order_tags': None, 'order_splits': []}"""
