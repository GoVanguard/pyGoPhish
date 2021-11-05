# Generated by Django 3.2.8 on 2021-11-03 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pondering', '0002_rename_domain_domain_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='phishingtrip',
            name='domain',
        ),
        migrations.RemoveField(
            model_name='phishingtripinstance',
            name='authority',
        ),
        migrations.AddField(
            model_name='phishingtrip',
            name='authority',
            field=models.CharField(blank=True, help_text='GoVanguard employee authorizing the phishing campaign.', max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='phishingtrip',
            name='company',
            field=models.CharField(blank=True, help_text='Company that contracted GoVanguard for a phishing campaign.', max_length=32, null=True),
        ),
    ]
