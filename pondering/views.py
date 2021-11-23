import logging
import uuid
from dateutil import tz, parser
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import generic
from pondering.models import PhishingWebsite, TargetWebsite, PhishingTrip, PhishingTripInstance, PhishingEmail
from pondering.models import PointOfContact, Company, Owner
from pondering.authhelper import getSignInFlow, getTokenFromCode, storeUser, removeUserAndToken, getToken
from pondering.graphhelper import getUser
from pondering.forms import DomainScheduler
from django.core.exceptions import FieldError
from django.db.utils import IntegrityError

def root(request):
    # Redirect clients accessing the service from a non-standard path.
    return redirect('http://localhost:8000/home')


def home(request):
    context = initializeContext(request)
    return render(request, 'pondering/home.html', context)


def initializeContext(request):
    context = {}
    # Check for any errors in the session
    error = request.session.pop('flash_error', None)
    if error != None:
        context['errors'] = []
        context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context


def signIn(request):
    # Get the sign-in flow
    flow = getSignInFlow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])


def goPhishing(request):
    context = initializeContext(request)
    context = getPhishingContext(context)
    if request.method == 'POST':
        context = postPhishingContext(request, context)
        return HttpResponseRedirect(reverse('schedule'))
    return render(request, 'pondering/gophish.html', context=context)


def emailSetup(request):
    context = initializeContext(request)
    context = getEmailContext(context)
    if request.method == 'POST':
        context = postCampaignContext(request, context)
        return HTTPResponseRedirect(reverse('schedule'))
    return render(request, 'pondering/campaignsetup.html', context=context)


def getPhishingContext(context):
    context['csrfmiddlewaretoken'] = ''
    context['company'] = ''
    context['poc'] = ''
    context['owner'] = ''
    context['phishingwebsite'] = ''
    context['targetwebsite'] = ''
    context['targets'] = None 
    context['datetime'] = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M')
    return context


def getEmailContext(context):
    context['csrfmiddlwaretoken'] = ''
    context['targetwebsite'] = ''
    context['targetemailaddress'] = ''
    context['phishingemailaddress'] = ''
    context['testemailaddress'] = ''
    context['subject'] = ''
    context['body'] = ''


def postPhishingContext(request, context):
    context.update(request.POST.dict()) 
    phishingForm = DomainScheduler(request.POST, request.FILES)
    print(phishingForm.errors)
    if phishingForm.is_valid():
        logging.info("The data provided by {0} is valid.".format(getClientIp(request)))
        data = phishingForm.cleaned_data
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
    location = None
    try:
        location = PhishingWebsite.objects.filter(url__iexact=url)
    except FieldError as exc:
        logging.error('No phishing websites exist: {0}'.format(exc))
        logging.info('Generating first phishing website: {0}'.format(url))
        location = PhishingWebsite()
        location.url = url
    else:
        result = location.first()
        if result is None:
            location = createPhishingWebsite(url)
        else:
            location = result
    finally:
        location.save()
        return location


def filterTargetWebsite(url):
    location = None 
    try:
        location = TargetWebsite.objects.filter(url__iexact=url)
    except FieldError as exc:
        logging.error('No target websites exist: {0}'.format(exc))
        logging.info('Generating first target website.')
        location = TargetWebsite()
        location.url = url
    else:
        result = location.first()
        if result is None:
            location = createTargetWebsite(url)
        else:
            location = result
    finally:
        location.save()
        return location


def filterPhishingTripInstance(trip, pond, target, targets, time):
    if targets:
        for tar in targets:
            filterPhishingTripInstanceHelper(trip, pond, tar, time)
    if target:
        filterPhishingTripInstanceHelper(trip, pond, target, time)


def filterPhishingTripInstanceHelper(trip, pond, target, time):
    tripInstance = None
    try:
        tripInstance = PhishingTripInstance.objects.filter(target__url__iexact=target).filter(datetime__iexact=time)
    except FieldError as exc:
        logging.error('No phishing trip instances exist: {0}'.format(exc))
        logging.info('Generating first phishing trip instance.')
        tripInstance = createPhishingTripInstance(trip, pond, target, targets, time)
    except IntegrityError as exc:
        logging.error('A duplicate phishing trip exists: {0}'.format(exc))
    else:
        result = tripInstance.first()
        if result is None:
            tripInstance = createPhishingTripInstance(trip, pond, target, time)
            tripInstance.save()


def filterPhishingTrip(company, poc, owner):
    trip = None
    try:
        trip = PhishingTrip.objects.filter(company__name__iexact=company).filter(owner__name__iexact=owner).filter(company__poc__name__iexact=poc)
    except FieldError as exc:
        logging.error('No phishing trips exist: {0}'.format(exc))
        logging.info('Generating first phishing trip.')
        trip = createPhishingTrip(company, poc, owner)
    else:
        result = trip.first()
        if result is None:
            trip = createPhishingTrip(company, poc, owner)
        else:
            trip = trip.first()
    finally:
        trip.save()
        return trip


def filterCompany(company, poc):
    c = None
    try:
        c = Company.objects.filter(name__iexact=company).filter(poc__name__iexact=poc)
    except:
        logging.error('No companies exist: {0}'.format(exc))
        logging.info('Generating first company.')
    else:
        result = c.first()
        if result is None:
            c = createCompany(company, poc)
        else:
            c = result 
    finally:
        c.save()
        return c


def filterPointOfContact(name):
    poc = None
    try:
        poc = PointOfContact.objects.filter(name__iexact=name)
    except:
        logging.error('No points of contact exist: {0}'.format(exc))
        logging.info('Generating first point of contact.')
        poc = createPointOfContact(name)
    else:
        result = poc.first()
        if result is None:
            poc = createPointOfContact(name)
        else:
            poc = result 
    finally:
        poc.save()
        return poc


def filterOwner(name):
    owner = None
    try:
        owner = Owner.objects.filter(name__iexact=name)
    except:
        logging.error('No points of contact exist: {0}'.format(exc))
        logging.info('Generating first point of contact.')
        owner = createOwner(name)
    else:
        result = owner.first()
        if result is None:
            owner = createOwner(name)
        else:
            owner = result 
    finally:
        owner.save()
        return owner


def filterTargets(websites):
    pass


def createPointOfContact(name):
    poc = PointOfContact()
    poc.name = name
    return poc


def createCompany(company, poc):
    c = Company()
    c.name = company
    c.poc = filterPointOfContact(poc)
    return c


def createOwner(name):
    owner = Owner()
    owner.name = name
    return owner


def createPhishingWebsite(url):
    website = PhishingWebsite()
    website.url = url
    return website


def createTargetWebsite(url):
    website = TargetWebsite()
    website.url = url
    return website


def createPhishingTrip(company, poc, owner):
    trip = PhishingTrip()
    trip.company = filterCompany(company, poc)
    trip.owner = filterOwner(owner)
    return trip


def createPhishingTripInstance(trip, pond, target, time):
    tripInstance = PhishingTripInstance()
    tripInstance.target_id = uuid.uuid4()
    tripInstance.trip = trip
    tripInstance.pond = pond
    tripInstance.target = target
    tripInstance.datetime = time
    tripInstance.schedulingStatus = 'p'
    tripInstance.operationalStatus = 'a'
    return tripInstance


def schedule(request):
    context = initializeContext(request)
    return render(request, 'pondering/schedule.html', context=context)


def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def callback(request):
    # Make the token request
    result = getTokenFromCode(request)
    # Get the user's profile
    user = getUser(result['access_token'])
    # Store user
    storeUser(request, user)
    return HttpResponseRedirect(reverse('home'))


def signOut(request):
    # Delete the user and token
    removeUserAndToken(request)
    return HttpResponseRedirect(reverse('home'))


class PhishingTripListView(generic.ListView):
    model = PhishingTripInstance
       
    def get_queryset(self):
        return PhishingTripInstance.objects.all()


class PhishingTripDetailView(generic.DetailView):
    model = PhishingTripInstance
