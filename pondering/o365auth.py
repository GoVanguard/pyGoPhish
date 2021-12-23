from O365 import Account
import yaml
from django.shortcuts import redirect

class AuthHelper:
    # Load the oauthsettings.yml file
    stream = open('oauthsettings.yml', 'r')
    settings = yaml.load(stream, yaml.SafeLoader)
    authState = {}

    def o365Authenticate():
        callback = 'http://localhost:8000/callback'
        account = Account((AuthHelper.settings['o365_id'], AuthHelper.settings['o365_secret']))
        url, state = account.con.get_authorization_url(requested_scopes=AuthHelper.settings['authority'], redirect_uri=callback)
        AuthHelper.authState = state
        return redirect(url)

    def o365Verify(request):
        print(request)
        account = Account((AuthHelper.settings['o365_id'], AuthHelper.settings['o365_secret']))
        state = AuthHelper.authState
        callback = 'http://localhost:8000/callback'
        result = account.con.request_token(request.url, state=state, redirect_uri=callback)
        return result
