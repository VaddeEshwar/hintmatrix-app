# Generated by Django 3.1.13 on 2021-09-11 18:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("question", "0012_delete_examevent"),
    ]

    operations = [
        migrations.AddField(
            model_name="examquestion",
            name="amount2",
            field=models.FloatField(default=0),
        ),
    ]
