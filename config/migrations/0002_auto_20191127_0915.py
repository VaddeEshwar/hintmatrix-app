# Generated by Django 2.2.4 on 2019-11-27 09:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tableheader",
            options={"ordering": ("-u_on",)},
        ),
    ]
