import logging
import requests
from uuid import uuid4
from requests import ConnectionError
from datetime import datetime, timezone, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from socket import gaierror

class DomainScheduler(forms.Form):
    company = forms.CharField(label='company', max_length=32)
    poc = forms.CharField(label='poc', max_length=32)
    owner = forms.CharField(label='owner', max_length=32)
    phishingwebsite = forms.CharField(label='phishingwebsite', max_length=2048)
    hyperlink = forms.CharField(label='hyperlink', max_length=4096)
    targetwebsite = forms.URLField(label='targetwebsite', max_length=2048)
    targets = forms.FileField(label='targets', max_length=32, allow_empty_file=True, required=False)
    datetime = forms.DateTimeField(label='datetime')

    def clean_company(self):
        data = self.cleaned_data['company']
        
        # TODO: Write a method to check for and remove special characters and reduce white space.
        
        return data

    def clean_poc(self):
        data = self.cleaned_data['poc']
        # TODO: Write a method to check for and remove special characters and reduce white space.
        
        return data

    def clean_owner(self):
        data = self.cleaned_data['owner']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_phishingwebsite(self):
        data = self.cleaned_data['phishingwebsite']
        return self.scrubURL(data)


    def clean_targetwebsite(self):
        data = self.cleaned_data['targetwebsite']
        return self.scrubURL(data)

    def clean_targets(self):
        targets = self.cleaned_data['targets']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return targets

    def clean_datetime(self):
        data = self.cleaned_data['datetime']
        
        # Generate UTC based datetime object.
        utcTime = datetime.now()

        # Generate a timezone aware datetime object.
        timeAware = datetime(utcTime.year, utcTime.month, utcTime.day, utcTime.hour, utcTime.minute, utcTime.second, utcTime.microsecond, tzinfo=timezone.utc)
        
        # Check if a date is not in the past.
        if data < timeAware:
            logging.warning('User scheduled an event in the past.')
            raise ValidationError(_('Invalid date - the scheduled time is in the past.'))
        # Check if a date is in the allowed range (+1 year from today).
        if data > timeAware + timedelta(weeks=52):
            logging.warning('User scheduled an event over a year from now.')
            raise ValidationError(_('Invalid date - the scheduled time is in the wrong year.'))
        # Remember to always return the cleaned data.
        return data


    def scrubURL(self, data):
        # Check if user prepended information.
        temp = data.split('.')

        if 'https://www' in temp:
            data = data[12:]
        
        if 'http://www' in temp:
            data = data[11:]
        
        temp = data.split('.')
        
        if 'https://' in temp:
            data = data[8:]

        if 'http://' in temp:
            data = data[7:]

        temp = data.split('.')

        if 'www.' in temp:
            data = data[4:]
        
        return data

class DomainNarrative(forms.Form):
    """Form for drafting phishing emails."""
    SMTP = 'SMTP'
    MICROSOFT_GRAPH = 'GRPH'
    OFFICE_365 = 'O365'
    SERVICE_CHOICES = [
        (SMTP, 'Simple Mail Transfer Protocol'),
        (MICROSOFT_GRAPH, 'Microsoft Graph'),
        (OFFICE_365, 'Microsoft Office 365'),
    ]
    service = forms.CharField(
        label='Service',
        min_length=4,
        max_length=4,
    )
    LINKED_IN = 'LI2U'
    GRAPH_IO = 'GRIO'
    GOVANGUARD = 'GOVD'
    ENUMERATION_CHOICES = [
        (LINKED_IN, 'LinkedIn2Username'),
        (GRAPH_IO, 'Graph IO'),
        (GOVANGUARD, 'GoVanguard Email Enumeration'),
    ]
    enumeration = forms.CharField(
        label='Enumerate',
        min_length=4,
        max_length=4,
    ) 
    phishingtrip = forms.UUIDField(label='id', required=True)
    to = forms.EmailField(label='to', max_length=320)
    cc = forms.EmailField(label='cc', max_length=320)
    efrom = forms.EmailField(label='efrom', max_length=320)
    domain = forms.URLField(label='domain', required=False, max_length=2048)
    subject = forms.CharField(label='subject', max_length=998)
    keyword = forms.CharField(label='keyword', max_length=20)
    attachment = forms.FileField(label='attachment', required=False)
    body = forms.CharField(label='body', max_length=10000)

    def clean_phishingTrip(self):
        data = self.cleaned_data['phishingtrip']
        return data


    def clean_service(self):
        data = self.cleaned_data['service']
        return [choice[0] for choice in self.SERVICE_CHOICES if data == choice[0]][0]

    def clean_enumeration(self):
        data = self.cleaned_data['enumeration']
        return data

    def clean_domain(self):
        data = self.cleaned_data['domain']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_efrom(self):
        data = self.cleaned_data['efrom']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_to(self):
        data = self.cleaned_data['to']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data
    
    def clean_subject(self):
        data = self.cleaned_data['subject']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_keyword(self):
        data = self.cleaned_data['keyword']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_attachment(self):
        data = self.cleaned_data['attachment']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_body(self):
        data = self.cleaned_data['body']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data


class CompanyProfile(forms.Form):
    """Form for filtering information related to the target company."""
    instance = forms.UUIDField(label='instance', required=False)
    company = forms.CharField(label='company', required=False, max_length=200)
    exclusion = forms.CharField(label='exclusion', required=False, max_length=1017)
    inclusion = forms.CharField(label='inclusion', required=False, max_length=1017)

    def clean_instance(self):
        data = self.cleaned_data['instance']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_company(self):
        data = self.cleaned_data['company']
        
        # TODO: Write a method to check for and remove special characters and reduce white space.
        
        return data

    def clean_exclusion(self):
        data = self.cleaned_data['exclusion']

        # TODO: Write a method to check for and remove special characters and reduce white space.
        
        return data
