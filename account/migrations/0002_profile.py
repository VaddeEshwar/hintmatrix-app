# Generated by Django 3.1.4 on 2022-06-15 05:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0037_state'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, help_text='row id', unique=True)),
                ('is_active', models.PositiveSmallIntegerField(default=0, verbose_name='active row')),
                ('status', models.PositiveIntegerField(default=0, verbose_name='row status')),
                ('c_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('u_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('mobile', models.CharField(max_length=10, null=True)),
                ('is_wa_number', models.BooleanField(default=False)),
                ('address', models.CharField(max_length=512, null=True)),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='config.state')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-u_on',),
                'abstract': False,
            },
        ),
    ]
