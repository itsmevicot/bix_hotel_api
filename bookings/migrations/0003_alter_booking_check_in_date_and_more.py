# Generated by Django 5.1.2 on 2024-10-29 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='check_in_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='booking',
            name='check_out_date',
            field=models.DateField(),
        ),
    ]