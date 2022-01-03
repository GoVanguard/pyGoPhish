# Generated by Django 3.2.8 on 2021-12-29 21:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('pondering', '0004_auto_20211227_1353'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GoPhishing',
        ),
        migrations.AlterField(
            model_name='phishingtripinstance',
            name='id',
            field=models.UUIDField(default=uuid.UUID('0e1987b6-6ed2-4d14-af34-2c5f43fe1916'), help_text='Unique ID for this particular phishing trip.', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='targetemailaddress',
            name='id',
            field=models.UUIDField(default=uuid.UUID('1442d23c-d313-437c-8466-c08bffae3bb0'), help_text='Unique ID for this particular e-mail address.', primary_key=True, serialize=False),
        ),
    ]
