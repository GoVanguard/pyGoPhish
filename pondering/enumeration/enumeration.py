"""PyGoPhish e-mail enumeration business logic."""
# Built-in imports
import logging

# LinkedIn2Username imports
from pondering.LiIn2User import linkedin2username

# PyGoPhish imports
from pondering.email import email 
from pondering import models

def getEnumerationContext(request, context):
    pk = request.GET.get('id')
    instance = models.PhishingTripInstance.objects.filter(pk=pk).first()
    print(instance.email.objects.all())
    enumeration = instance.email.enumeration
    if enumeration == 'LI2U':
        context.update({'LI2U': True})
    return context


def discoverLI2U(request, context):
    company = context['Company']
    creds = AuthHelper.getLi2UserCredentials()
    session = linkedin2username.login(creds)
    if not session:
        logging.Error('LinkedIn2Username failed to login with the credentials provided.')
    else:
        session = linkedin2username.set_search_csrf(session)
        companyId, staffCount = linkedin2username.get_company_info(company, session)
        context.update({'CompanyId': companyId, 'StaffCount': staffCount})
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
