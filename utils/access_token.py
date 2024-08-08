import time
from typing import Dict, Callable

import jwt
from django.conf import settings
from itsdangerous import TimestampSigner


def generate_access_token(
    user_id: str,
    email: str,
    optional_data: Dict = None,
) -> str:
    """
    :param user_id: user name
    :param email: email of login user
    :param optional_data: if any extra data
    :return: access token
    """
    if optional_data is None:
        optional_data = {}

    issued_at = int(time.time())
    access_token = {
        "eml": email,
        "uid": user_id,
        "iat": issued_at,
    }
    if optional_data:
        access_token = access_token | optional_data
    access_token = jwt.encode(access_token, key=settings.JWT_SECRET_KEY)
    signer = TimestampSigner(settings.JWT_SECRET_KEY)
    access_token = signer.sign(access_token).decode("utf-8")
    return access_token


def validate_access_token(func: Callable) -> Callable:
    """
    decarator for validate token
    :param func:
    :return:
    """

    def validate(_, info, **kwargs):
        access_token = info.context.access_token
        if not access_token:
            raise
            # return not_allowed(
            #     permission="Token",
            #     message_key="invalid-token",
            #     message="Token required to access",
            # )

        s = TimestampSigner(settings.JWT_SECRET_KEY)
        is_token_valid = s.validate(
            access_token, max_age=settings.TOKEN_EXPIRY_IN_MINUTES * 60
        )
        if not is_token_valid:
            raise
            # return not_allowed(
            #     permission="Token",
            #     message_key="invalid-token",
            #     message="Token is not valid anymore",
            # )

        decoded_token = jwt.decode(
            s.unsign(
                access_token, max_age=settings.TOKEN_EXPIRY_IN_MINUTES * 60
            ).decode("utf-8"),
            key=settings.JWT_SECRET_KEY,
            algorithms="HS256",
        )
        print(decoded_token)
        # user_id = decoded_token.get("uid")
        # info.context.user_id = user_id
        # info.context.user_email = decoded_token.get("eml")
        return func(_, info, **kwargs)

    return validate
