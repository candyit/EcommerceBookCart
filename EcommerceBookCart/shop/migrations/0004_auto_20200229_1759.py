# Generated by Django 3.0.3 on 2020-02-29 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20200229_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
