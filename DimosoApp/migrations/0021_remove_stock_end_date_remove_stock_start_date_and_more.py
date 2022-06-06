# Generated by Django 4.0.3 on 2022-05-07 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DimosoApp', '0020_alter_stock_end_date_alter_stock_last_updated_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='start_date',
        ),
        migrations.AddField(
            model_name='stock',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
