# Generated by Django 3.2.8 on 2021-11-02 20:32

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.URLField(help_text='Enter a URL.')),
            ],
        ),
        migrations.CreateModel(
            name='PhishingTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.ManyToManyField(help_text='Enter a domain.', to='pondering.Domain')),
            ],
        ),
        migrations.CreateModel(
            name='PhishingTripInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular phishing trip.', primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField(max_length=20)),
                ('authority', models.CharField(blank=True, max_length=32, null=True)),
                ('status', models.CharField(blank=True, choices=[('p', 'Pending'), ('r', 'Requesting Approval'), ('a', 'Approved')], default='p', help_text='Phishing campaign status.', max_length=1)),
                ('trip', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.phishingtrip')),
            ],
            options={
                'ordering': ['datetime'],
            },
        ),
    ]