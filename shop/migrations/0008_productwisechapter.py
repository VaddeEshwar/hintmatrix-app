# Generated by Django 3.1.4 on 2023-06-23 19:39

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0040_auto_20220709_0221'),
        ('shop', '0007_auto_20220815_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductWiseChapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, help_text='row id', unique=True)),
                ('is_active', models.PositiveSmallIntegerField(default=0, verbose_name='active row')),
                ('status', models.PositiveIntegerField(default=0, verbose_name='row status')),
                ('c_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('u_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('code', models.CharField(max_length=8)),
                ('chapter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='config.chapter')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.product')),
            ],
            options={
                'ordering': ('c_on', 'code'),
            },
        ),
    ]
