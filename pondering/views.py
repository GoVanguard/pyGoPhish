"""Router for PyGoPhish WSGI application."""
# Built-in imports
import logging
import uuid
import time
import pprint
from dateutil import tz, parser
from smtplib import SMTP
from smtplib import SMTPException
from smtplib import SMTPConnectError

# Django Web Application Framework imports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import generic

# Dnspython imports
from dns import resolver

# LinkedIn2Username imports
from pondering.LiIn2User import linkedin2username

# PyGoPhish imports
from pondering import models 
from pondering.gophish import gophish 
from pondering.email import email 
from pondering.authhelper import AuthHelper 
from pondering.graphhelper import getUser
from pondering.enumeration import enumeration


def root(request):
    # Redirect clients accessing the service from a non-standard path.
    return redirect('http://localhost:8000/home')


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


def home(request):
    context = initializeContext(request)
    return render(request, 'pondering/home.html', context)


def signIn(request):
    # Get the sign-in flow
    flow = AuthHelper.getSignInFlow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])


def goPhish(request):
    context = initializeContext(request)
    context = gophish.getPhishingContext(context)
    if request.method == 'POST':
        context = gophish.postPhishingContext(request, context)
        return HttpResponseRedirect(reverse('schedule'))
    return render(request, 'pondering/gophish.html', context=context)


def emailSetup(request):
    context = initializeContext(request)
    phishingTrip = models.PhishingTripInstance()
    if request.method == 'GET':
        context = email.getEmailContext(request, context)
    if request.method == 'POST':
        context = email.postEmailContext(request, context)
        pk = context['Instance']
        return HttpResponseRedirect('enumerate?id={0}'.format(pk))
    return render(request, 'pondering/email.html', context=context)


def emailTest(request):
    context = initializeContext(request)
    if request.method == 'POST':
        context = Email.postEmailContext(request, context)
        service = context['Service']
        if service == 'SMTP':
            context = Email.emailSMTP(request, context)
            return render(request, 'pondering/test.html', context=context)
        if service == 'GRPH':
            context = Email.emailGRPH(request, context)
            return render(request, 'pondering/test.html', context=context)
        if service == 'O365':
            context = Email.emailO365(request, context)
            return render(request, 'pondering/test.html', context=context)


def enumerate(request):
    context = initializeContext(request)
    if request.method == 'GET':
        context = enumeration.getEnumerationContext(request, context) 
        return render(request, 'pondering/enumerate.html', context)
    if request.method == 'POST':
        context = Email.postEnumerateContext(request, context)
        return render(request, 'pondering/enumerate.html', context) 


def schedule(request):
    context = initializeContext(request)
    return render(request, 'pondering/schedule.html', context=context)


def callback(request):
    # Make the token request
    result = AuthHelper.getTokenFromCode(request)
    # Get the user's profile
    user = getUser(result['access_token'])
    # Store user
    AuthHelper.storeUser(request, user)
    return HttpResponseRedirect(reverse('home'))


def signOut(request):
    # Delete the user and token
    AuthHelper.removeUserAndToken(request)
    # Return the user to the home page
    return HttpResponseRedirect(reverse('home'))


class PhishingListView(generic.ListView):
    # Set the model for the generic.ListView object template
    model = models.PhishingList

    def get_queryset(self):
       """Abstract template function that populates the list based on the specified phishing trip."""
       # Return a list of the emails associated with a Phishing Trip Instance
       return models.PhishingList.objects.all() 


class PhishingTripListView(generic.ListView):
    # Set the model for the generic.ListView object template
    model = models.PhishingTripInstance

    def get_queryset(self):
        """Abstract template function that populates the list."""
        # Return a list of Phishing Trip Instances
        return models.PhishingTripInstance.objects.all()


class PhishingTripDetailView(generic.DetailView):
    model = models.PhishingTripInstance 
