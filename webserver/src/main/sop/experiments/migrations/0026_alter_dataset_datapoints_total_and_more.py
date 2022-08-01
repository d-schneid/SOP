# Generated by Django 4.0.6 on 2022-08-01 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0025_alter_execution_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='datapoints_total',
            field=models.PositiveBigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='dimensions_total',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='execution',
            name='subspace_amount',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='execution',
            name='subspaces_max',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='execution',
            name='subspaces_min',
            field=models.PositiveIntegerField(),
        ),
    ]
