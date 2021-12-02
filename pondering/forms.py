import logging
import requests
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
    phishingwebsite = forms.URLField(label='phishingwebsite', max_length=2048)
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
        userInput = self.cleaned_data['phishingwebsite']
        data = self.cleaned_data['phishingwebsite']
        return self.scrubURL(userInput, data)


    def clean_targetwebsite(self):
        userInput = self.cleaned_data['targetwebsite']
        data = self.cleaned_data['targetwebsite']
        return self.scrubURL(userInput, data)


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


    def scrubURL(self, userInput, data):
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
        
        try:
            # Check if the domain responds to a ping request.
            response = requests.get(data)
        except ConnectionError as err:
            # Note if the destination or network connection are not reachable.
            logging.error('The network connection to {0} timed out. Either the resource does not exist or the destination is not reachable (try again after verifying your url dns listing).'.format(data))
        except gaierror as err:
            # Note if we are too impatient with the request.
            logging.error('Requests library did not await domain resolution.')
        else: 
            # Validate the URL
            if response.status_code == 200 or 300 or 301 or 302 or 308:
                # TODO: Handle redirects, update the url, and perform a recursive callback on the new destination.
                pass
            else:
                logging.warning('User attempted entering the following URL: {0}'.format(user_input))
                logging.warning('http://{0} is not listed or does not allow GET requests.'.format(user_input))
        finally:
            return data

class DomainNarrative(forms.Form):
    """Form for drafting phishing emails."""
    domain = forms.URLField(label='domain', required=False, max_length=2048)
    emailFrom = forms.EmailField(label='emailFrom', max_length=320)
    preview = forms.EmailField(label='preview', max_length=320)
    subject = forms.CharField(label='subject', max_length=998)
    body = forms.CharField(label='body', max_length=10000)
    keyword = forms.CharField(label='keyword', max_length=20)

    SMTP = 'SMTP'
    MICROSOFT_GRAPH = 'GRAPH'
    OFFICE_365 = 'O365'
    SERVICE_CHOICES = [
        (SMTP, 'Simple Mail Transfer Protocol'),
        (MICROSOFT_GRAPH, 'Microsoft Graph'),
        (OFFICE_365, 'Microsoft Office 365'),
    ]
    service = forms.CharField(
        min_length=4,
        max_length=4,
    )

    def clean_domain(self):
        data = self.cleaned_data['domain']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_emailFrom(self):
        data = self.cleaned_data['emailFrom']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_preview(self):
        data = self.cleaned_data['preview']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data
    
    def clean_subject(self):
        data = self.cleaned_data['subject']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_body(self):
        data = self.cleaned_data['body']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_keyword(self):
        data = self.cleaned_data['keyword']

        # TODO: Write a method to check for and remove special characters and reduce white space.

        return data

    def clean_service(self):
        data = self.cleaned_data['service']
        if data in self.SERVICE_CHOICES:
            print('Match')
        return data
