# Generated by Django 5.2.3 on 2025-06-26 02:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0006_user_last_login_user_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='user',
            name='password',
        ),
    ]
