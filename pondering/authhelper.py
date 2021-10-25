import yaml
import msal
import os
import time

# Load the oauthsettings.yml file
stream = open('oauthsettings.yml', 'r')
settings = yaml.load(stream, yaml.SafeLoader)

def loadCache(request):
    # Check for a token cache in the session
    cache = msal.SerializableTokenCache()
    if request.session.get('token_cache'):
        cache.deserialize(request.session['token_cache'])
    return cache

def saveCache(request, cache):
    # If cache has changed, persist back to session
    if cache.has_state_changed:
        request.session['token_cache'] = cache.serialize()

def getMSALApp(cache=None):
    # Initialize the MSAL confidential client
    authApp = msal.ConfidentialClientApplication(
        settings['app_id'],
        authority=settings['authority'],
        client_credential=settings['app_secret'],
        token_cache=cache
    )
    return authApp

# Method to generate a sign-in flow
def getSignInFlow():
    authApp = getMSALApp()
    return authApp.initiate_auth_code_flow(
        settings['scopes'],
        redirect_uri=settings['redirect']
    )

# Method to exchange auth code for access token
def getTokenFromCode(request):
    cache = loadCache(request)
    authApp = getMSALApp(cache)
    # Get the flow saved in session
    flow = request.session.pop('auth_flow', {})
    result = authApp.acquire_token_by_auth_code_flow(flow, request.GET)
    saveCache(request, cache)
    return result

def storeUser(request, user):
    try:
        request.session['user'] = {
            'is_authenticated': True,
            'name': user['displayName'],
            'email': user['mail'] if (user['mail'] != None) else user['userPrincipalName'],
            'timeZone': user['mailboxSettings']['timeZone'] if (user['mailboxSettings']['timeZone'] != None) else 'UTC'
        }
    except Exception as e:
        print(e)

def getToken(request):
    cache = loadCache(request)
    authApp = getMSALApp(cache)
    accounts = authApp.get_accounts()
    if accounts:
        result = authApp.acquire_token_silent(
            settings['scopes'],
            account=accounts[0]
        )
        save_cache(request, cache)
    return result['access_token']

def removeUserAndToken(request):
    if 'token_cache' in request.session:
        del request.session['token_cache']
    if 'user' in request.session:
        del request.session['user']
