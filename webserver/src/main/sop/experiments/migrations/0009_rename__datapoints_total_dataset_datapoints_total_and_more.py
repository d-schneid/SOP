# Generated by Django 4.0.6 on 2022-07-07 11:21

import django.core.validators
from django.db import migrations, models
import experiments.models.dataset


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0008_alter_dataset_managers_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='_datapoints_total',
            new_name='datapoints_total',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='_dimensions_total',
            new_name='dimensions_total',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='_user',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='dataset',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='dataset',
            name='description',
            field=models.TextField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='dataset',
            name='is_cleaned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dataset',
            name='path_cleaned',
            field=models.FileField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='dataset',
            name='path_original',
            field=models.FileField(default=0, upload_to=experiments.models.dataset._get_dataset_upload_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv'])]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='algorithm',
            name='group',
            field=models.CharField(choices=[('Probabilistic', 'Probabilistic'), ('Linear Model', 'Linear Model'), ('Proximity-Based', 'Proximity Based'), ('Outlier Ensembles', 'Outlier Ensembles'), ('Neural Networks', 'Neural Networks'), ('Combination', 'Combination'), ('Other', 'Other')], max_length=80),
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='_description',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='_is_cleaned',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='_path_cleaned',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='_path_original',
        ),
    ]
