from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from dateutil import tz, parser
from datetime import datetime, timedelta
from pondering.authhelper import getSignInFlow, getTokenFromCode, storeUser, removeUserAndToken, getToken
from pondering.graphhelper import getUser

def root(request):
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
    return render(request, 'pondering/gophish.html', context)

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
