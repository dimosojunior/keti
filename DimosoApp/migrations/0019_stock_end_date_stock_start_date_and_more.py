# Generated by Django 4.0.3 on 2022-05-06 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DimosoApp', '0018_remove_stock_end_date_remove_stock_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateField(auto_now=True, null=True),
        ),
    ]
