# Generated by Django 4.0.6 on 2022-07-22 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0022_alter_execution_subspace_generation_seed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='display_name',
            field=models.CharField(max_length=80, verbose_name='Experiment'),
        ),
    ]
