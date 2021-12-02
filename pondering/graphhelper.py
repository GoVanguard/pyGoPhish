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

def getMyMail(token):
    # Set headers
    headers = {
            'Authorization': 'Bearer {0}'.format(token)
    }

    # Configure query parameters to modify the results
    queryParams = {
        '$orderby': 'receivedDateTime'
    }

    # Send get to /me/
    mail = requests.get('{0}/me/mailfolders/inbox/messages'.format(graphURL),
        headers=headers,
        params=queryParams)

    return mail.json()

def sendMail(token, subject, body, toRecipients, ccRecipients):
    # Set headers
    headers = {
            'Authorization': 'Bearer {0}'.format(token),
            'Content-type': 'application/json'
    }

    # Configure query parameters to modify the results
    queryParams = {
        '$orderby': 'receivedDateTime'
    }

    # Send get to the appropriate user
    body = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "Text",
                        "content": body
                    },
                "toRecipients": toRecipients,
                "ccRecipients": ccRecipients,
                },
                "saveToSentItems": "false"
            }
    response = requests.post('{0}/me/sendMail'.format(graphURL),
        headers = headers,
        body = body)
    return response
