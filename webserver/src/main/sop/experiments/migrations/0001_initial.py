# Generated by Django 4.0.5 on 2022-07-04 01:00

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import experiments.models
import experiments.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AlgorithmModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_name', models.CharField(max_length=80)),
                ('_group', models.CharField(choices=[('Linear Model', 'Linear Model'), ('Proximity-based', 'Proximity Based'), ('Probabilistic', 'Probabilistic'), ('Outlier Ensembles', 'Outlier Ensembles'), ('Other', 'Other')], max_length=80)),
                ('_signature', models.CharField(max_length=80)),
                ('_path', models.FileField(upload_to=experiments.models.get_algorithm_upload_path, validators=[experiments.validators.validate_file_extension, django.core.validators.FileExtensionValidator(allowed_extensions=['.py'])])),
                ('_description', models.TextField()),
                ('_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('_name', '_user')},
            },
        ),
        migrations.CreateModel(
            name='DatasetModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_display_name', models.CharField(max_length=80)),
                ('_creation_date', models.DateTimeField(auto_now_add=True)),
                ('_algorithms', models.ManyToManyField(to='experiments.algorithmmodel')),
                ('_dataset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='experiment', to='experiments.datasetmodel')),
                ('_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('_display_name', '_user')},
            },
        ),
    ]
