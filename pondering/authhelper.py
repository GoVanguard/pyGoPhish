import yaml
import msal
import os
import time

class args:
    username = ''
    password = ''
    company = ''
    proxy = False
    geoblast = False
    depth = False
    keywords = False
    sleep = 0

class AuthHelper:
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
            AuthHelper.settings['client_id'],
            authority=AuthHelper.settings['authority'],
            client_credential=AuthHelper.settings['client_secret'],
            token_cache=cache
        )
        return authApp

    # Method to generate a sign-in flow
    def getSignInFlow():
        authApp = AuthHelper.getMSALApp()
        return authApp.initiate_auth_code_flow(
            AuthHelper.settings['scopes'],
            redirect_uri=AuthHelper.settings['redirect']
        )

    # Method to exchange auth code for access token
    def getTokenFromCode(request):
        cache = AuthHelper.loadCache(request)
        authApp = AuthHelper.getMSALApp(cache)
        # Get the flow saved in session
        flow = request.session.pop('auth_flow', {})
        result = authApp.acquire_token_by_auth_code_flow(flow, request.GET)
        AuthHelper.saveCache(request, cache)
        return result

    def getLi2UserCredentials():
        creds = args()
        creds.username = AuthHelper.settings['linkedin_username']
        creds.password = AuthHelper.settings['linkedin_password']
        creds.proxy = False
        return creds

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
        cache = AuthHelper.loadCache(request)
        authApp = AuthHelper.getMSALApp(cache)
        accounts = authApp.get_accounts()
        if accounts:
            result = authApp.acquire_token_silent(
                AuthHelper.settings['scopes'],
                account=accounts[0]
            )
            AuthHelper.saveCache(request, cache)
        return result['access_token']

    def removeUserAndToken(request):
        if 'token_cache' in request.session:
            del request.session['token_cache']
        if 'user' in request.session:
            del request.session['user']

