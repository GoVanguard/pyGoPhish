import logging
import uuid
import time
import pprint
from dns import resolver
from smtplib import SMTP
from smtplib import SMTPException
from smtplib import SMTPConnectError
from dateutil import tz, parser
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import generic
from pondering.models import GoPhishing
from pondering.gophish.gophish import GoPhish
from pondering.email.email import Email
from pondering.authhelper import AuthHelper 
from pondering.graphhelper import getUser  

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
    context = GoPhish.getPhishingContext(context)
    if request.method == 'POST':
        context = GoPhish.postPhishingContext(request, context)
        return HttpResponseRedirect(reverse('schedule'))
    return render(request, 'pondering/gophish.html', context=context)


def emailSetup(request):
    context = initializeContext(request)
    context = Email.getEmailContext(context)
    if request.method == 'POST':
        context = postEmailContext(request, context)
        return HttpResponseRedirect(reverse('settings'))
    return render(request, 'pondering/email.html', context=context)


def emailTest(request):
    context = initializeContext(request)
    context = Email.getEmailContext(context)
    if request.method == 'POST':
        context = Email.postEmailContext(request, context)
        return Email.generateTestEmailSMTP(request, context)  
    return render(request, 'pondering/email.html', context=context)


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


class PhishingTripListView(generic.ListView):
    # Set the model for the generic.ListView object template
    model = GoPhishing.PhishingTripInstance

    def get_queryset(self):
        """Abstract template function that populates the list."""
        # Return a list of Phishing Trip Instances
        return GoPhishing.PhishingTripInstance.objects.all()


class PhishingTripDetailView(generic.DetailView):
    model = GoPhishing.PhishingTripInstance 
