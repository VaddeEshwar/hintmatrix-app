import requests

from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import resolve_url

from utils.message.fire_email import FireEmail


def shoot_activation_email(user):
    # print("shoot_activation_email")
    # print(user)
    from_email = f"Welcome Mail <no-reply-{uuid4().__str__()}@hintmatrix.com>"
    fr = FireEmail(
        action="welcome", to_email=user.email,
        from_email=from_email, from_name="Welcome Mail")
    cache_id = uuid4().__str__()
    cache.set(cache_id, user.email, 86400)
    url_path = resolve_url("website_v2:signup-activate", cache_id=cache_id)
    # print(url_path)
    url = f"{settings.APPLICATION_BASE_URL}{url_path}"
    data = dict(activate_url=url)
    return fr.shoot_email(data)


def shoot_forgot_password_email(user):
    # print("shoot_forgot_password_email")
    # print(user)
    from_email = f"Forgot Password <forgot-{uuid4().__str__()}@hintmatrix.com>"
    fr = FireEmail(
        action="forgot_password", to_email=user.email,
        from_email=from_email, from_name="forgot password")
    cache_id = uuid4().__str__()
    cache.set(cache_id, user.email, 86400)
    url_path = resolve_url("website_v2:forgot-password-set", cache_id=cache_id)
    # print(url_path)
    url = f"{settings.APPLICATION_BASE_URL}{url_path}"
    data = dict(
        user_email=user.email,
        forgot_password_url=url
    )
    return fr.shoot_email(data)


def verify_email(email):
    """
    https://api.elasticemail.com/v2/email/verify?
    apikey=7H29A61A88F5D6F1CX5CC79IWQADW3EFC98CD5F4428W7WU2B873256BCECCDCIAP8
    A5C4JS6A29675XHFBED2DFCDF9I1QW&
    email=mail@example.com&
    uploadContact=&
    updateStatus=
    :return:
    """
    url = "https://api.elasticemail.com/v2/email/verify"
    data = dict(
        apikey=settings.ELASTICEMAIL_API_KEY,
        email=email,
        uploadContact=True,
        updateStatus=True
    )

    ve = requests.post(url, data)
    res = ve.json()
    """
    {'success': True, 'data': {'account': 'ff.jonnala', 'domain': 'gmail.com',
    'email': 'ff.jonnala@gmail.com', 'suggestedspelling': '',
    'disposable': False, 'role': False, 'reason': '', 'result': 'Valid'}}
    """

    if res.get("data", {}).get('result') == "Valid":
        return True
    return False
