# Generated by Django 2.2.4 on 2019-11-27 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="examquestion",
            name="name",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
