# Generated by Django 4.0.5 on 2022-07-04 21:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("experiments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasetmodel",
            name="_datapoints_total",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datasetmodel",
            name="_description",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datasetmodel",
            name="_dimensions_total",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datasetmodel",
            name="_is_cleaned",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datasetmodel",
            name="_name",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datasetmodel",
            name="_path_cleaned",
            field=models.FilePathField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datasetmodel",
            name="_path_original",
            field=models.FileField(default="", upload_to=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datasetmodel",
            name="_user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
