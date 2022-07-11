# Generated by Django 4.0.6 on 2022-07-08 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0015_execution_algorithm_parameters_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="execution",
            name="experiment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="experiments.experiment"
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="dataset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="experiments.dataset"
            ),
        ),
    ]
