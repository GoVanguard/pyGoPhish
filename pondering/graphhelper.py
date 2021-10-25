import requests
import json

graphURL = 'https://graph.microsoft.com/v1.0'

def getUser(token):
    # Send GET to /me
    user = requests.get(
        '{0}/me'.format(graphURL),
        headers={
            'Authorization': 'Bearer {0}'.format(token)
        },
        params={
            '$select': 'displayName,mail,mailboxSettings,userPrincipalName'
        })
    # Return the JSON result
    return user.json()
