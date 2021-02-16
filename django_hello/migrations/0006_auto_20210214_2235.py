# Generated by Django 3.1.6 on 2021-02-14 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_studentexamaccess_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentexamaccess',
            name='has_attended',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='studentexamaccess',
            name='score',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]