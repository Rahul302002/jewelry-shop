# Generated by Django 4.1.7 on 2024-02-25 12:51

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0017_vendor_alter_userhistoryviewproduct_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userhistoryviewproduct',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 25, 12, 51, 47, 101124, tzinfo=datetime.timezone.utc)),
        ),
    ]
