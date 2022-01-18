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
from rest_framework.decorators import api_view

# Dnspython imports
from dns import resolver

# LinkedIn2Username imports
from pondering.LiIn2User import linkedin2username

# PyGoPhish imports
from pondering import models 
from pondering import authhelper 
from pondering.gophish import gophish 
from pondering.email import email 
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
    flow = authhelper.getSignInFlow()
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
        return render(request, 'pondering/email.html', context=context)
    if request.method == 'POST':
        context = email.postEmailContext(request, context)
        if 'Instance' in context.keys():
            pk = context['Instance']
            return HttpResponseRedirect('enumerate?id={0}'.format(pk))
        else:
            return HttpResponseRedirect('gophish')


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


@api_view(['GET','POST'])
def enumerate(request):
    context = initializeContext(request)
    if request.method == 'GET':
        context = enumeration.getEnumerationContext(request, context)
        return render(request, 'pondering/enumerate.html', context)
    if request.method == 'POST':
        keys = request.POST.keys()
        if 'inclusion' in keys or 'exclusion' in keys:
            context = enumeration.deleteEnumerationContext(request, context)
        else:
            context = enumeration.postEnumerationContext(request, context)
        return render(request, 'pondering/linkedinresults.html', context) 

def schedule(request):
    context = initializeContext(request)
    return render(request, 'pondering/schedule.html', context=context)


def callback(request):
    # Make the token request
    result = authhelper.getTokenFromCode(request)
    # Get the user's profile
    user = getUser(result['access_token'])
    # Store user
    authhelper.storeUser(request, user)
    return HttpResponseRedirect(reverse('home'))


def signOut(request):
    # Delete the user and token
    authhelper.removeUserAndToken(request)
    # Return the user to the home page
    return HttpResponseRedirect(reverse('home'))


class PhishingListView(generic.ListView):
    # Set the model for the generic.ListView object template
    model = models.PhishingList

    def get_context_data(self):
        context = initializeContext(self.request)
        return context

    def get_queryset(self):
       """Abstract template function that populates the list based on the specified phishing trip."""
       # Return a list of the emails associated with a Phishing Trip Instance
       return models.PhishingList.objects.all() 


class PhishingTripListView(generic.ListView):
    # Set the model for the generic.ListView object template
    model = models.PhishingTripInstance

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get the context for this view."""
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        context.update(initializeContext(self.request))
        return super().get_context_data(**context)

    def get_queryset(self):
        """Abstract template function that populates the list."""
        # Return a list of Phishing Trip Instances
        return models.PhishingTripInstance.objects.all()


class PhishingTripDetailView(generic.DetailView):
    model = models.PhishingTripInstance 

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get the context for this view."""
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        context.update(initializeContext(self.request))
        return super().get_context_data(**context)

