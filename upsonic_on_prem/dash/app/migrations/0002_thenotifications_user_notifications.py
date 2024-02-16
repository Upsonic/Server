# Generated by Django 4.2.9 on 2024-02-16 12:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TheNotifications',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('message', models.CharField(max_length=1000)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('important', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='notifications',
            field=models.ManyToManyField(blank=True, to='app.thenotifications'),
        ),
    ]
