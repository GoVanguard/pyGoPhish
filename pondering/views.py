import logging
from dateutil import tz, parser
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import generic
from .models import Domain, PhishingTrip, PhishingTripInstance
from pondering.authhelper import getSignInFlow, getTokenFromCode, storeUser, removeUserAndToken, getToken
from pondering.graphhelper import getUser
from pondering.forms import DomainScheduler
from pondering.models import Domain, PhishingTrip, PhishingTripInstance


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
        contxt = postPhishingContext(request, context)
        return HttpResponseRedirect(reverse('schedule'))
    return render(request, 'pondering/gophish.html', context=context)

def getPhishingContext(context):
    context['csrfmiddlewaretoken'] = ''
    context['company'] = ''
    context['poc'] = ''
    context['url'] = ''
    context['datetime'] = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M')
    return context


def postPhishingContext(request, context):
    context.update(request.POST.dict()) 
    phishingForm = DomainScheduler(request.POST)
    result = phishingForm.is_valid()
    print(phishingForm.errors)
    if phishingForm.is_valid():
        logging.info("Domain and date are valid from: {0}".format(getClientIp(request)))
        data = phishingForm.cleaned_data
        domain = filterDomain(data['domain'])
        location = filterPhishingTrip(data['company'], data['poc'])
        time = data['datetime']
        event = PhishingTripInstance()
        filterDomainCR(event, location, time, domain) 
        context.update(data)
        return context
    else:
        logging.warning('Client has deliberately circumvented JavaScript input filtering.')
        logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
        return context 

def filterDomain(url):
    location = Domain()
    if Domain.objects.filter(url__icontains=url):
        location = Domain.objects.filter(url__icontains=url).first()
    else:
        location.url = url 
        location.save()
    return location

def filterPhishingTrip(company, poc):
    trip = PhishingTrip()
    if PhishingTrip.objects.filter(company__icontains=company).filter(poc__icontains=poc):
            trip = PhishingTrip.objects.filter(company__icontains=company).filter(poc__icontains=poc).first()
    else:
        trip.company = company
        trip.poc = poc 
        trip.save()
    return trip

def filterDomainCR(event, location, time, domain):
    event.trip = location
    event.datetime = time 
    event.save()
    if PhishingTripInstance.objects.filter(domain__url=domain.url):
        pass
    else:
        event.domain = domain
        event.save()
    

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
