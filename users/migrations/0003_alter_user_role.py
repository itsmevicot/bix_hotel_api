# Generated by Django 5.1.2 on 2024-10-30 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('CLIENT', 'Client'), ('STAFF', 'Staff'), ('ADMIN', 'Admin')], default='CLIENT', max_length=20),
        ),
    ]
