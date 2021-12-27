# Generated by Django 3.2.8 on 2021-12-03 19:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('pondering', '0015_auto_20211203_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phishingtripinstance',
            name='id',
            field=models.UUIDField(default=uuid.UUID('3db2de88-a134-4070-9ade-191869f062fd'), help_text='Unique ID for this particular phishing trip.', primary_key=True, serialize=False),
        ),
    ]