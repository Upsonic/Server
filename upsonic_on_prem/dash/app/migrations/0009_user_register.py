# Generated by Django 4.2.9 on 2024-07-11 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_user_dark_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='register',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]