# Generated by Django 5.1.2 on 2024-10-29 02:28

import django.contrib.auth.models
import django.core.validators
import localflavor.br.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(error_messages={'unique': 'A user with this email already exists.'}, max_length=254, unique=True, validators=[django.core.validators.EmailValidator(message='Enter a valid email address.')])),
                ('cpf', localflavor.br.models.BRCPFField(error_messages={'unique': 'A user with this CPF already exists.'}, max_length=14, unique=True)),
                ('birth_date', models.DateField()),
                ('role', models.CharField(choices=[('CLIENT', 'Client'), ('STAFF', 'Staff'), ('MANAGER', 'Manager'), ('ADMIN', 'Admin')], default='CLIENT', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]