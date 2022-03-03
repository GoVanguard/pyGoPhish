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

def sendMail(token, email):
    # Set headers
    headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Content-type': 'application/json'
    }

    response = requests.post('{0}/me/sendMail'.format(graphURL),
        headers = headers,
        data = email)
    return response

def sendMailHelper(toEmailList):
    returnList = []
    if type(toEmailList) == list:
        for email in toEmailList:
            returnList.append({"emailAddress":{"address": email}})
    elif type(toEmailList) == str and toEmailList:
        returnList = [{"emailAddress":{"address": toEmailList}}]
    else:
        returnList = [{"emailAddress":{"address": "info@example.com"}}]
    return returnList
