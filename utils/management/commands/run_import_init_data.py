from django.core.management.base import BaseCommand

from config.models import RuleEngine1, RuleEngine


class Command(BaseCommand):
    help = "Import data Tenant DB"

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         'tenant_id', type=str, help="Enter Tenant id")

    def handle(self, *args, **options):
        # _eng_q_set = FinalRuleEngineCsv.objects.all().values(
        #     'attribute_code', 'atribute_name').order_by(
        #     "atribute_name")
        # for _e in _eng_q_set:
        #     print(_e)
        #     _data = dict(
        #         code=_e.get("attribute_code"),
        #         name=_e.get("atribute_name"),
        #         short_name=_e.get("atribute_name"))
        #     print(_data)
        #     TableAttribute(**_data).save()

        _re1 = (
            RuleEngine1.objects.all()
            .values(
                "relationship",
                "operation1",
                "help1",
                "operation2",
                "help2",
                "header1_id",
                "header2_id",
                "pair_attr_id",
                "tbl1_id",
                "tbl2_id",
                "tbl_attribute_id",
                "pair_attr_priority",
            )
            .order_by("tbl_attribute_id")
        )
        for _re in _re1:
            print(_re)
            RuleEngine(**_re).save()

        self.stdout.write(self.style.SUCCESS("Successfully created admin role."))
