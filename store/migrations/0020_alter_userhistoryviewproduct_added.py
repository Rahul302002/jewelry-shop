# Generated by Django 4.1.7 on 2024-02-29 05:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_userhistoryviewproduct_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userhistoryviewproduct',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 29, 5, 59, 42, 756667, tzinfo=datetime.timezone.utc)),
        ),
    ]
