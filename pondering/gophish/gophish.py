"""Business logic for the phishing campaign registration process."""
# Built-in imports
import logging
import uuid
from datetime import datetime, timedelta

# PyGoPhish imports
from pondering.logginghelper import getClientIp
from pondering.forms import DomainScheduler
from pondering import models 

# Django framework error imports
from django.core.exceptions import FieldError
from django.db.utils import IntegrityError, OperationalError


def getPhishingContext(context):
    """Phishing context initializer."""
    context['company'] = ''
    context['poc'] = ''
    context['owner'] = ''
    context['phishingwebsite'] = ''
    context['targetwebsite'] = ''
    context['targets'] = None 
    context['datetime'] = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M')
    return context


def postPhishingContext(request, context):
    """Phishing context handler."""
    domainForm = DomainScheduler(request.POST, request.FILES)
    if domainForm.is_valid():
        logging.info("The data provided by {0} to the domain scheduler is valid.".format(getClientIp(request)))
        data = domainForm.cleaned_data
        trip = filterPhishingTrip(data['company'], data['poc'], data['owner'])
        pond = filterPhishingWebsite(data['phishingwebsite'])
        target = filterTargetWebsite(data['targetwebsite'])
        targets = filterTargets(data['targets'])
        time = data['datetime']
        filterPhishingTripInstance(trip, pond, target, targets, time)
        context.update(data)
        return context
    else:
        logging.warning('Client has deliberately circumvented JavaScript input filtering.')
        logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
        return context


def filterPhishingWebsite(url):
    """Phishing website duplication filter."""
    location = None
    try:
        location = GoPhishing.PhishingWebsite.objects.filter(url__iexact=url)
    except FieldError as exc:
        logging.error('No phishing websites exist: {0}'.format(exc))
        logging.info('Generating first phishing website: {0}'.format(url))
        location = GoPhishing.PhishingWebsite()
        location.url = url
    else:
        result = location.first()
        if result is None:
            location = GoPhish.createPhishingWebsite(url)
        else:
            location = result
    finally:
        location.save()
        return location


def filterTargetWebsite(url):
    """Target website duplication filter."""
    location = None 
    try:
        location = GoPhishing.TargetWebsite.objects.filter(url__iexact=url)
    except FieldError as exc:
        logging.error('No target websites exist: {0}'.format(exc))
        logging.info('Generating first target website.')
        location = GoPhishing.TargetWebsite()
        location.url = url
    else:
        result = location.first()
        if result is None:
            location = GoPhish.createTargetWebsite(url)
        else:
            location = result
    finally:
        location.save()
        return location


def filterPhishingTripInstance(trip, pond, target, targets, time):
    if targets:
        for tar in targets:
            GoPhish.filterPhishingTripInstanceHelper(trip, pond, tar, time)
    if target:
        GoPhish.filterPhishingTripInstanceHelper(trip, pond, target, time)

# TODO: Fix the time formatting so that you can query events based on time.
def filterPhishingTripInstanceHelper(trip, pond, target, time):
    tripInstance = None
    try:
        tripInstance = GoPhishing.objects.filter(pond__url__iexact=pond).filter(target__url__iexact=target)
    except FieldError as exc:
        logging.error('No phishing trip instances exist: {0}'.format(exc))
        logging.info('Generating first phishing trip instance.')
        tripInstance = GoPhish.createPhishingTripInstance(trip, pond, target, targets, time)
    except IntegrityError as exc:
        logging.error('A duplicate phishing trip exists: {0}'.format(exc))
    else:
        result = tripInstance.first()
        if result is None:
            tripInstance = GoPhish.createPhishingTripInstance(trip, pond, target, time)
            tripInstance.save()


def filterPhishingTrip(company, poc, owner):
    trip = None
    try:
        trip = models.PhishingTrip.objects.filter(company__name__iexact=company).filter(owner__name__iexact=owner).filter(company__poc__name__iexact=poc)
    except OperationalError as exc:
        logging.error('The phishing trip table does not exist {0}'.format(exc))
        logging.info('Stop the server, delete the db.sqliteX database file, delete all the migrations folders and files inside all Django applications, run python manage.py makemigrations, run python manage.py migrate, run python manage.py makemigrations appname, and finally run python manage.py migrate appname. This should resolve the operational error that generates no such table for your application.')
        trip = gophish.createPhishingTrip(company, poc, owner)
    except FieldError as exc:
        logging.error('No phishing trips exist: {0}'.format(exc))
        logging.info('Generating first phishing trip.')
        trip = gophish.createPhishingTrip(company, poc, owner)
    else:
        logging.info('No exception triggered in filterPhishingTrip')
        result = trip.first()
        if result is None:
            logging.warning('Result is none in filterPhishingTrip')
            trip = gophish.createPhishingTrip(company, poc, owner)
        else:
            trip = result 
    finally:
        trip.save()
        return trip


def filterCompany(company, poc):
    c = None
    try:
        c = GoPhishing.Company.objects.filter(name__iexact=company).filter(poc__name__iexact=poc)
    except:
        logging.error('No companies exist: {0}'.format(exc))
        logging.info('Generating first company.')
    else:
        result = c.first()
        if result is None:
            c = GoPhish.createCompany(company, poc)
        else:
            c = result 
    finally:
        c.save()
        return c


def filterPointOfContact(name):
    poc = None
    try:
        poc = GoPhishing.PointOfContact.objects.filter(name__iexact=name)
    except:
        logging.error('No points of contact exist: {0}'.format(exc))
        logging.info('Generating first point of contact.')
        poc = GoPhish.createPointOfContact(name)
    else:
        result = poc.first()
        if result is None:
            poc = GoPhish.createPointOfContact(name)
        else:
            poc = result 
    finally:
        poc.save()
        return poc


def filterOwner(name):
    owner = None
    try:
        owner = GoPhishing.Owner.objects.filter(name__iexact=name)
    except:
        logging.error('No points of contact exist: {0}'.format(exc))
        logging.info('Generating first point of contact.')
        owner = GoPhish.createOwner(name)
    else:
        result = owner.first()
        if result is None:
            owner = GoPhish.createOwner(name)
        else:
            owner = result 
    finally:
        owner.save()
        return owner


def filterTargets(websites):
    pass


def createPointOfContact(name):
    poc = GoPhishing.PointOfContact()
    poc.name = name
    return poc


def createCompany(company, poc):
    c = GoPhishing.Company()
    c.name = company
    c.poc = GoPhish.filterPointOfContact(poc)
    return c


def createOwner(name):
    owner = GoPhishing.Owner()
    owner.name = name
    return owner


def createPhishingWebsite(url):
    website = GoPhishing.PhishingWebsite()
    website.url = url
    return website


def createTargetWebsite(url):
    website = GoPhishing.TargetWebsite()
    website.url = url
    return website


def createPhishingTrip(company, poc, owner):
    trip = GoPhishing.PhishingTrip()
    trip.company = GoPhish.filterCompany(company, poc)
    trip.owner = GoPhish.filterOwner(owner)
    return trip


def createPhishingTripInstance(trip, pond, target, time):
    tripInstance = GoPhishing()
    tripInstance.id = uuid.uuid4()
    tripInstance.trip = trip
    tripInstance.pond = pond
    tripInstance.target = target
    tripInstance.datetime = time
    tripInstance.schedulingStatus = 'p'
    tripInstance.operationalStatus = 'a'
    return tripInstance
