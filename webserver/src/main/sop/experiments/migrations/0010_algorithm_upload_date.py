# Generated by Django 4.0.6 on 2022-07-07 11:38

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "experiments",
            "0009_rename__datapoints_total_dataset_datapoints_total_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="algorithm",
            name="upload_date",
            field=models.DateField(default=datetime.date.today),
        ),
    ]
