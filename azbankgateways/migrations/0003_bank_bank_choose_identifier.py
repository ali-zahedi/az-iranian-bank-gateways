# Generated by Django 3.1.4 on 2021-01-04 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("azbankgateways", "0002_auto_20210102_0721"),
    ]

    operations = [
        migrations.AddField(
            model_name="bank",
            name="bank_choose_identifier",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Bank choose identifier",
            ),
        ),
    ]