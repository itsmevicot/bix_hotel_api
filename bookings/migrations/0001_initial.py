# Generated by Django 5.1.2 on 2024-10-29 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateTimeField()),
                ('check_out_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled'), ('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='CONFIRMED', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
