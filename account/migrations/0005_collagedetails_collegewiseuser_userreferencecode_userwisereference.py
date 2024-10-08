# Generated by Django 3.1.4 on 2022-12-27 17:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('config', '0040_auto_20220709_0221'),
        ('account', '0004_invoice_invoiceitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollageDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, help_text='row id', unique=True)),
                ('is_active', models.PositiveSmallIntegerField(default=0, verbose_name='active row')),
                ('status', models.PositiveIntegerField(default=0, verbose_name='row status')),
                ('c_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('u_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('code', models.CharField(max_length=16, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('contact_no', models.CharField(max_length=10, null=True, verbose_name='Contact Number')),
                ('wa_number', models.CharField(max_length=16, null=True, verbose_name='Whatsapp Mobile No')),
                ('address', models.CharField(max_length=512, null=True, verbose_name='address')),
                ('admin_user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='config.state', verbose_name='state')),
            ],
            options={
                'ordering': ('-u_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserWiseReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, help_text='row id', unique=True)),
                ('is_active', models.PositiveSmallIntegerField(default=0, verbose_name='active row')),
                ('status', models.PositiveIntegerField(default=0, verbose_name='row status')),
                ('c_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('u_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('referral_code', models.CharField(max_length=16)),
                ('username', models.CharField(max_length=256)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-u_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserReferenceCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, help_text='row id', unique=True)),
                ('is_active', models.PositiveSmallIntegerField(default=0, verbose_name='active row')),
                ('status', models.PositiveIntegerField(default=0, verbose_name='row status')),
                ('c_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('u_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('referral_code', models.CharField(max_length=16)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-u_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollegeWiseUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, help_text='row id', unique=True)),
                ('is_active', models.PositiveSmallIntegerField(default=0, verbose_name='active row')),
                ('status', models.PositiveIntegerField(default=0, verbose_name='row status')),
                ('c_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('u_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('username', models.CharField(max_length=256)),
                ('college', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.collagedetails')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-u_on',),
                'abstract': False,
            },
        ),
    ]
