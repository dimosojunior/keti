# Generated by Django 4.0.3 on 2022-06-04 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DimosoApp', '0037_alter_stock_created_alter_stock_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.IntegerField(blank=True, default='0', null=True)),
                ('email', models.EmailField(blank=True, default='0', max_length=254, null=True)),
                ('place', models.CharField(blank=True, max_length=200, null=True)),
                ('username', models.CharField(blank=True, max_length=200, null=True)),
                ('send_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
