# Generated by Django 4.0.6 on 2022-07-11 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0017_alter_algorithm_upload_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="algorithm",
            name="display_name",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="dataset",
            name="display_name",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
    ]
