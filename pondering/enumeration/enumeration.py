"""PyGoPhish e-mail enumeration business logic."""
# Built-in imports
import logging
import json

# LinkedIn2Username imports
from pondering.LiIn2User import linkedin2username

# PyGoPhish imports
from pondering.logginghelper import getClientIp
from pondering.email import email 
from pondering.forms import CompanyProfile
from pondering import authhelper
from pondering import models

def getEnumerationContext(request, context):
    instance = request.GET.get('id')
    enumeration = 'LI2U'
    if instance:
        phishingTrip = models.PhishingTripInstance.objects.filter(pk=instance).first()
        if phishingTrip is not None:
            enumeration = instance.email.enumeration
    if enumeration == 'LI2U':
        context.update({'LI2U': True})
    return context


def postEnumerationContext(request, context):
    context = getEnumerationContext(request, context)
    companyProfile = CompanyProfile(request.POST)
    if companyProfile.is_valid():
        logging.info('The data provided by {0} to the company profile is valid.'.format(getClientIp(request)))
        data = companyProfile.cleaned_data
        liname = data['company']
        update = {'Company': liname}
        context.update(update)
        discoverLI2U(request, context)
        return context
    else:
        if companyProfile.errors:
            logging.error(companyProfile.errors)
        logging.warning('Client has deliberately circumvented JavaScript input filtering.')
        logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
    return context


def discoverLI2U(request, context):
    company = context['Company']
    session = authhelper.li2UserLogin()
    if not session:
        logging.error('LinkedIn2Username failed to login with the credentials provided.')
    else:
        session = linkedin2username.set_search_csrf(session)
        companyId, staffCount = linkedin2username.get_company_info(company, session)
        context.update({'CompanyId': companyId, 'StaffCount': staffCount})
    print(context)
    return context


def enumerateLI2U(request, context):
    address = context['Domain']
    company = context['Company']
    if not session:
        logging.Error('LinkedIn2Username failed to login with the credentials provided.')
    else:
        session = linkedin2username.set_search_csrf(session)
        companyId, staffCount = linkedin2username.get_company_info(company, session)
        foundNames = linkedin2username.scrape_info(session, companyId, staffCount, creds)
        cleanList = linkedin2username.clean(foundNames)
        emaiilList = linkedin2username.write_list(company, address, cleanList)
        return context


def filterEnumerationContext(request, context):
    """Enumeration duplication filter."""
