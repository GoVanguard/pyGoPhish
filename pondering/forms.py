import logging
import requests
from datetime import datetime, timezone, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from socket import gaierror 

class DomainScheduler(forms.Form):
    company = forms.CharField(label='Company', max_length=32)
    poc = forms.CharField(label='POC', max_length=32)
    domain = forms.URLField(label='Domain', max_length=2048)
    datetime = forms.DateTimeField(label='Event')

    def clean_company(self):
        user_input = self.cleaned_data['company']
        data = self.cleaned_data['company']
        
        # TODO: Write a method to check for and remove special characters, reduce white space, and replace spaces with hyphens.
        
        return data

    def clean_poc(self):
        user_input = self.cleaned_data['poc']
        data = self.cleaned_data['poc']
        # TODO: Write a method to check for and remove special characters, reduce white space, and replace spaces with hyphens.
        
        return data

    def clean_domain(self):
        user_input = self.cleaned_data['domain']
        data = self.cleaned_data['domain']

        # Check if user prepended information.
        temp = data.split('.')

        if 'http://www' in temp:
            data = data[11:]
        
        temp = data.split('.')

        if 'http://' in temp:
            data = data[7:]

        temp = data.split('.')

        if 'www' in temp:
            data = data[4:]
        
        try:
            # Check if a domain responds to a ping request.
            response = requests.get(data)
        except gaierror:
            # Note if we are too impatient with the request.
            logging.error('Requests library did not await domain resolution.')
       
        # Validate the URL
        if response.status_code == 200 or 300 or 301 or 302 or 308:
            # TODO: Handle redirects and update the url.
            pass
        else:
            logging.error('User attempted entering the following URL: {0}'.format(user_input))
            logging.error('http://{0} does not allow GET requests.'.format(user_input))
            raise ValidationError(_('The domain did not respond.'))
        return data

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
