import logging

from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from utils.message.shoot_email_support import shoot_activation_email

# Get an instance of a logger
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=User)
def set_new_user_inactive(sender, instance, **kwargs):
    print("set_new_user_inactive")
    if instance._state.adding is True:
        print("Creating Inactive User")
        if not instance.email:
            instance.email = instance.username
        instance.is_active = False
    print("end set_new_user_inactive")


@receiver(post_save, sender=User)
def shoot_user_activation_email(sender, instance, **kwargs):
    # send welcome email to username or email.
    print("shoot_user_activation_email")
    # user not active and never logged in.
    if not instance.is_active and not instance.last_login:
        print("activate email sending.")
        try:
            if not shoot_activation_email(instance):
                print(f"welcome email not able to send {instance.email}.")
                logger.warning(
                    f"welcome email not able to send {instance.email}.")
            else:
                print(f"welcome email able sent to {instance.email}.")
                logger.info(f"welcome email able sent to {instance.email}.")
                # Note: Due to email receivable issue, for the time, we are
                # activating account.
                instance.is_active = True
                instance.save()
        except Exception as e:
            logger.error(e.__str__())
            print(40, e.__str__())
    print("end shoot_user_activation_email")
