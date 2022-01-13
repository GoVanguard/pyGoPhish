"""PyGoPhish e-mail enumeration business logic."""
# Built-in imports
import os
import logging
import json
from uuid import UUID

# LinkedIn2Username imports
from pondering.LiIn2User import linkedin2username

# Django Q imports
from django_q.tasks import async_task, result

# Django framework imports
from django.http import HttpResponseRedirect

# Django framework error imports
from django.core.exceptions import FieldError

# PyGoPhish imports
from pondering.logginghelper import getClientIp
from pondering.email import email 
from pondering.forms import CompanyProfile
from pondering import authhelper
from pondering import models


creds = {'session': None, 'username': '', 'password': '', 'company': '', 'proxy': False, 'geoblast': False, 'depth': False, 'keywords': False, 'sleep': 0, 'depth': False}
linkedInLogin = async_task(authhelper.li2UserLogin, creds, sync=True)
global linkedInSession
linkedInSession = result(linkedInLogin, 200)

def getEnumerationContext(request, context):
    """Method for GET requests to the enumerate view."""
    logging.info('Entering pondering.enumerate.enumerate.getEnumerationContext')
    instance = request.GET.get('id')
    if instance:
        if UUID(instance, version=4):
            context['Instance'] = instance
        else:
            logging.warning('Client is attempting parameter fuzzing.')
    logging.info('Exiting pondering.enumerate.enumerate.getEnumerationContext')
    return context


def postEnumerationContext(request, context):
    """Method for POST requests to the enumerate view."""
    logging.info('Entering pondering.enumerate.enumerate.postEnumerationContext.')
    context = refreshInstance(request, context)
    companyProfile = CompanyProfile(request.POST)
    if companyProfile.is_valid():
        logging.info('The data provided by {0} to the company profile is valid.'.format(getClientIp(request)))
        data = companyProfile.cleaned_data
        liname = data['company']
        info = {'Company': liname}
        context.update(info)
        if liname and 'accept' in request.POST.keys():
            context = enumerateLI2U(request, context) 
        else:
            context = discoverLI2U(request, context)
        logging.info('Exiting pondering.enumerate.enumerate.postEnumerationContext at branch CompanyProfile.is_valid() is True')
        return context
    else:
        if companyProfile.errors:
            logging.error(companyProfile.errors)
        logging.warning('Client has deliberately circumvented JavaScript input filtering.')
        logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
        logging.info('Exiting pondering.enumerate.enumerate.getEnumerationContext at branch CompanyProfile.is_valid() is False')
    return context


def deleteEnumerationContext(request, context):
    """Method for DELETE requests to the enumerate view."""
    logging.info('Entering pondering.enumerate.enumerate.deleteEnumerationContext')
    context = refreshInstance(request, context)
    if 'exclude' in context.keys():
        context = addExclusion(request, context)
    if 'include' in context.keys():
        context = removeExclusion(request, context)
    logging.info('Exiting pondering.enumerate.enumerate.deleteEnumerationContext')
    return context


def getInstance(request, context):
    """Method for obtaining the phishing campaign instance within the uWSGI context."""
    logging.info('Entering pondering.enumerate.enumerate.getInstance')
    instance = None
    if request.method == 'GET':
        temp = request.GET.get('id')
    if request.method == 'POST':
        temp = request.POST.get('instance')
        if UUID(temp, version=4):
            instance = temp
    if instance:
        phishingTripInstance = None
        try:
            phishingTripInstance = models.PhishingTripInstance.objects.filter(pk=instance).first()
        except FieldError as exc:
            logging.error('No phishing trip instances exist.')
        else:
            if not phishingTripInstance:
                logging.info('Exiting pondering.enumerate.enumerate.refreshInstance at branch models.PhishingTripInstance.objects.filter(pk).first() does not exist and returning context.')
                logging.info('Redirecting user to the gophish view')
                return HttpResponseRedirect('gophish')
        finally:
            return phishingTripInstance 


def refreshInstance(request, context):
    """Method for retaining the phishing campaign instance within the uWSGI context."""
    logging.info('Entering pondering.enumerate.enumerate.refreshInstance')
    instance = None
    temp = None 
    if request.method == 'GET':
        temp = request.GET.get('id')
    if request.method == 'POST':
        temp = request.POST.get('instance')
    if UUID(temp, version=4):
        instance = temp
    if instance:
        phishingTripInstance = None
        try:
            phishingTripInstance = models.PhishingTripInstance.objects.filter(pk=instance).first()
        except FieldError as exc:
            logging.error('No phishing trip instances exist.')
        else:
            if phishingTripInstance:
                enumeration = phishingTripInstance.email.enumeration
                domain = phishingTripInstance.target
                dbList = phishingTripInstance.nameList.text
                nameList = dbList.split('\n')
                exclusions = getExclusions()
                info = {'Instance': instance, 'Domain': domain, 'Enumeration': enumeration}
                if nameList:
                    info['Names'] = nameList
                if exclusions:
                    info['Exclusions'] = exclusions
                context.update(info)
                logging.info('Exiting pondering.enumerate.enumerate.refreshInstance at branch models.PhishingTripInstance.objects.filter(pk).first() exists and returning context.')
            else:
                logging.info('Exiting pondering.enumerate.enumerate.refreshInstance at branch models.PhishingTripInstance.objects.filter(pk).first() does not exist and returning context.')
                logging.info('Redirecting user to the gophish view')
                return HttpResponseRedirect('gophish')
        finally:
            return context
    else:
        logging.info('Exiting pondering.enumerate.enumerate.refreshInstance at branch models.PhishingTripInstance.objects.filter(pk).first() does not exist and returning context.')
        logging.info('Redirecting user to the gophish view')
        return HttpResponseRedirect('gophish')



def discoverLI2U(request, context):
    """Method for discovering businesses registered with LinkedIn."""
    logging.info('Entering pondering.enumerate.enumerate.discoverLI2U')
    global linkedInSesssion
    company = context['Company']
    if linkedInSession:
        linkedin2username.set_search_csrf(linkedInSession)
        companyId, staffCount = linkedin2username.get_company_info(company, linkedInSession)
        info = {'CompanyId': companyId, 'StaffCount': staffCount}
        context.update(info)
        logging.info('Exiting pondering.enumerate.enumerate.discoverLI2U at session is False and returning context.')
    else:
        logging.error('LinkedIn2Username failed to login with the credentials provided.')
        logging.info('Exiting pondering.enumerate.enumerate.discoverLI2U at session is True and returning context.')
    return context


def enumerateLI2U(request, context):
    """Method for enumerating employees registered with a business on LinkedIn."""
    logging.info('Entering pondering.enumerate.enumerate.enumerateLI2U')
    global linkedInSession
    address = context['Domain']
    company = context['Company']
    instance = context['Instance']
    phishingTripInstance = getInstance(request, context)
    if linkedInSession:
        logging.info('Entering pondering.enumerate.enumerate.enumerateLI2U at branch session is True.')
        linkedin2username.set_search_csrf(linkedInSession)
        companyId, staffCount = linkedin2username.get_company_info(company, linkedInSession)
        foundNames = linkedin2username.scrape_info(linkedInSession, companyId, staffCount, creds)
        cleanList = linkedin2username.clean(foundNames)
        staffFound = len(cleanList)
        nameList = filterNameList(phishingTripInstance, cleanList)
        info = {'CompanyId': companyId, 'StaffCount': staffCount, 'Names': nameList, 'StaffFound': staffFound, 'Percentage': format((staffFound/staffCount)*100, '.2g')}
        context.update(info)
        logging.info('Exiting pondering.enumerate.enumerate.enumerateLI2U at branch session is True and returning context.')
    else:
        logging.error('LinkedIn2Username failed to login with the credentials provided.')
        logging.info('Exiting pondering.enumerate.enumerate.enumerateLI2U at session is False and returning context.')
    return context


def addExclusion(request, context):
    """Method for adding an exclusion, updating the context, and returning the view."""
    logging.info('Entering pondering.enumerate.enumerate.addExclusion')
    companyProfile = companyProfile(request.POST)
    if companyProfile.is_valid():
        logging.info('The data provided by {0} to the company profile is valid.'.format(getClientIp(request)))
        data = companyProfile.cleaned_data
        exclusion = data['exclusion']
        filterExclusion(text)
    else:
        if companyProfile.errors:
            logging.error(companyProfile.errors)
        logging.warning('Client has deliberately circumvented JavaScript input filtering.')
        logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
        logging.info('Exiting pondering.enumerate.enumerate.addExclusion at branch CompanyProfile.is_valid() is False')
    logging.info('Exiting pondering.enumerate.enumerate.addExclusion')
    return context
    


def filterNameList(instance, cleanList):
    """Name list duplication filter."""
    logging.info('Entering pondering.enumerate.enumerate.filterNameList')
    text = '\n'.join(cleanList) 
    dbList = None
    try:
        dbList = models.NameList.objects.filter(text__iexact=text)
    except FieldError as exc:
        logging.error('No name lists exist: {0}'.format(exc))
        dbList = createNameList(text)
    else:
        result = dbList.first()
        if result:
            dbList = result
        else:
            dbList = createNameList(text)
    finally:
        dbList.save()
        instance.nameList = dbList
        instance.save()
        nameList = dbList.text.split('\n')
        exclusions = getExclusions()
        if not exclusions:
            exclusions = ['']
        for count, name in enumerate(nameList):
            splitName = name.split()
            for text in splitName:
                if text in exclusions:
                    splitName.remove(text)
                else:
                    filterName(text)
            nameList[count] = splitName
        return nameList


def filterName(text):
    """Enumeration duplication and exclusion filter."""
    logging.info('Entering pondering.enumerate.enumerate.filterName')
    name = None
    exclusions = getExclusions()
    if exclusions:
        if text in exclusions:
            return 
    try:
        name = models.Name.objects.filter(text__iexact=text)
    except FieldError as exc:
        logging.error('No names exist: {0}'.format(exc))
        logging.info('Generating first name: information redacted')
        name = createName(text)
    else:
        result = name.first()
        if result:
            name = result
        else:
            name = createName(text)
    finally:
        name.save()


def filterExclusion(text):
    """Exclusion duplication filter."""
    logging.info('Entering pondering.enumerate.enumerate.filterExclusion')
    exclusion = None
    try:
        exclusion = models.Exclusion.objects.filter(text__iexact=text)
    except FieldError as exc:
        logging.error('No exclusions exist: {0}'.format(exc))
        logging.info('Generating first exclusion: information redacted')
        result = createExclusion(text)
    else:
        result = exclusion.first()
        if result:
            return result
        else:
            result = createExclusion(text)
    finally:
        result.save()


def createNameList(text):
    """Method for creating a new name list instance."""
    nameList = models.NameList()
    nameList.text = text
    return nameList


def createName(text):
    """Method for creating a new name instance."""
    name = models.Name()
    name.text = text
    return name


def createExclusion(text):
    """Method for creating a new exclusion instance."""
    logging.info('Entering pondering.enumerate.enumerate.createExclusion')
    exclusion = models.Exclusions()
    exclusion.text = text
    exclusion.save()
    exclusions = models.Exclusions.objects.get_all()
    return exclusions


def getExclusions():
    """Method for retrieving the list of excluded terms."""
    logging.info('Entering pondering.enumerate.enumerate.getExclusions')
    exclusions = None
    try:
        exclusions = models.Exclusions.objects.get_all()
    except FieldError as exc:
        logging.error('No exclusions exist: {0}'.format(exc))
        logging.info('Generating a null value exclusion.')
        exclusions = createExclusion('')
    else:
        return exclusions
    finally:
        return [] 
