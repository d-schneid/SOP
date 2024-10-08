# Generated by Django 4.0.5 on 2022-07-04 22:23

import django.core.validators
from django.db import migrations, models

from experiments.models.algorithm import get_algorithm_upload_path


class Migration(migrations.Migration):
    dependencies = [
        ("experiments", "0003_rename_algorithmmodel_algorithm_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="algorithm",
            name="_path",
            field=models.FileField(
                upload_to=get_algorithm_upload_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["py"]
                    )
                ],
            ),
        ),
    ]
