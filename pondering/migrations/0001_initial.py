# Generated by Django 3.2.8 on 2021-11-19 20:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(blank=True, help_text='Company that contracted GoVanguard for a phishing campaign.', max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(blank=True, help_text='Owner of the social engineering campaign the company is contracting with GoVanguard.', max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhishingEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mailFrom', models.EmailField(blank=True, help_text='The e-mail address you are sending an e-mail from.', max_length=320, null=True)),
                ('preview', models.EmailField(blank=True, help_text='The e-mail address you want to preview the e-mail in.', max_length=320, null=True)),
                ('subject', models.CharField(blank=True, help_text='The subject for the phishing campaign e-mail.', max_length=998, null=True)),
                ('body', models.CharField(blank=True, help_text='The body of the phishing campaign e-mail.', max_length=10000, null=True)),
                ('keyword', models.CharField(blank=True, help_text='The template keyword used to substitute in the phishing domain.', max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhishingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PhishingTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(help_text='Company contracting the social engineering campaign from GoVanguard.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.company')),
            ],
        ),
        migrations.CreateModel(
            name='PhishingWebsite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(help_text='The phishing website.', max_length=2048)),
                ('hyperlink', models.CharField(blank=True, help_text='The hyperlink you want the phishing website to appear as.', max_length=2048, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PointOfContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poc', models.CharField(blank=True, help_text='Point of contact that knows the most about a specific company.', max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TargetEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, help_text='The e-mail address you are sending an e-mali to.', max_length=320, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TargetWebsite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(help_text='The client website that actively hosts a Simple Mail Transfer Protocol (SMTP) service.', max_length=2048)),
            ],
        ),
        migrations.CreateModel(
            name='PhishingTripInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular phishing trip.', primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField(max_length=20)),
                ('schedulingStatus', models.CharField(blank=True, choices=[('p', 'Pending'), ('s', 'Signed'), ('a', 'Approved')], default='p', help_text='Phishing campaign contract status.', max_length=1)),
                ('operationalSatus', models.CharField(blank=True, choices=[('i', 'Initializing'), ('r', 'Ready'), ('p', 'Phishing'), ('c', 'Complete'), ('e', 'Error')], default='p', help_text='Phishing campaign operational status.', max_length=1)),
                ('owner', models.ForeignKey(help_text='Owner of the social engineering campaign the company is contracting with GoVanguard.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.owner')),
                ('pond', models.OneToOneField(help_text='The phishing website.', null=True, on_delete=django.db.models.deletion.CASCADE, to='pondering.phishingwebsite')),
                ('target', models.OneToOneField(help_text='The client website that actively hosts a Simple Mail Transfer Protocol (SMTP) service.', null=True, on_delete=django.db.models.deletion.CASCADE, to='pondering.targetwebsite')),
                ('trip', models.ForeignKey(help_text='Create a phishing trip, which may include multiple domains.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.phishingtrip')),
            ],
            options={
                'ordering': ['datetime'],
            },
        ),
        migrations.AddField(
            model_name='phishingtrip',
            name='poc',
            field=models.ForeignKey(help_text='Point of contact within GoVanguard that knows the most about a specific company.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.pointofcontact'),
        ),
        migrations.CreateModel(
            name='PhishingResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phishingEmail', models.ForeignKey(help_text='The e-mail template for this phishing campaign.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.phishingemail')),
                ('phishingList', models.ForeignKey(help_text='List of e-mail addresses for this phishing campaign.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.phishinglist')),
                ('result', models.ForeignKey(help_text='An individual phishing campaign.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.phishingtripinstance')),
            ],
        ),
        migrations.AddField(
            model_name='phishinglist',
            name='phishingList',
            field=models.ForeignKey(help_text='Hyperlink representation of the phishing domain.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.targetemail'),
        ),
        migrations.AddField(
            model_name='phishingemail',
            name='mailTo',
            field=models.ForeignKey(blank=True, help_text='The e-mail address you are sending an e-mail to.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.targetemail'),
        ),
        migrations.AddField(
            model_name='phishingemail',
            name='targetWebsite',
            field=models.ForeignKey(help_text='Register the URL that actively hosts a Simple Mail Transfer Protocol (SMTP) service.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.targetwebsite'),
        ),
        migrations.AddField(
            model_name='company',
            name='poc',
            field=models.ForeignKey(help_text='Point of contact within GoVanguard that knows the most about a specific company.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pondering.pointofcontact'),
        ),
    ]
