from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = "account"
    # ignore import as signals to execute

    def ready(self):
        import account.signals  # noqa: F401
