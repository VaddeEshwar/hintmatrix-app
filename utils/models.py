from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


def make_field_dict(fld) -> dict:
    print(fld)
    if not fld.db_column:
        return {fld.attname: fld}
    return {fld.db_column: fld}


class AbstractModel(models.Model):
    class Meta:
        abstract = True
        ordering = ("-u_on",)

    # row alpha numeric slug
    slug = models.SlugField(
        default=uuid4, unique=True, help_text=_("row id"), editable=False
    )

    # status of record
    is_active = models.PositiveSmallIntegerField(default=0, verbose_name="active row")

    status = models.PositiveIntegerField(default=0, verbose_name=_("row status"))

    # record created on
    c_on = models.DateTimeField(auto_now_add=True, verbose_name="created on")
    # record updated on
    u_on = models.DateTimeField(auto_now=True, verbose_name="updated on")

    def __str__(self):
        return f"{self.slug}"

    @classmethod
    def get_queryset(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    @classmethod
    def get_related_fields(cls):
        # physical table name
        # cls._meta.db_table
        related_fields = {}
        for fld in cls._meta.get_fields():
            if not fld.related_model:
                continue
            # if user defined db_column at respected model field,
            # fld.db_column
            # else fld.attname
            related_fields.update(make_field_dict(fld))

        return related_fields

    @classmethod
    def get_fields(cls):
        fields = {}
        for fld in cls._meta.get_fields():
            if fld.related_model:
                continue
            fields.update(make_field_dict(fld))

        return fields

    @classmethod
    def get_all_fields(cls):
        fields = {}
        for fld in cls._meta.get_fields():
            fields.update(make_field_dict(fld))
        return fields
