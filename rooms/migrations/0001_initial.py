# Generated by Django 5.1.2 on 2024-10-30 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, unique=True)),
                ('type', models.CharField(choices=[('SINGLE', 'Single'), ('DOUBLE', 'Double'), ('SUITE', 'Suite')], max_length=20)),
                ('status', models.CharField(choices=[('AVAILABLE', 'Available'), ('BOOKED', 'Booked'), ('OCCUPIED', 'Occupied'), ('MAINTENANCE', 'Maintenance')], default='AVAILABLE', max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
