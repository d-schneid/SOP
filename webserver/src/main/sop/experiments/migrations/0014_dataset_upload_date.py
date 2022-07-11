# Generated by Django 4.0.6 on 2022-07-08 01:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0013_rename__algorithms_experiment_algorithms_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="upload_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
