# Generated by Django 3.2.8 on 2021-11-03 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pondering', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domain',
            old_name='domain',
            new_name='url',
        ),
    ]
