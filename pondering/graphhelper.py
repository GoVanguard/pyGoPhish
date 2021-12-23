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

def sendMail(token, subject, message, toRecipients, efrom, ccRecipients = ''):
    # Set headers
    headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Content-type': 'application/json'
    }

    email = {
    	"message": {
        	"subject": "Meet for lunch?",
            "body": {
                "contentType": "Text",
                "content": "The new cafeteria is open."
             },
            "toRecipients": [
                {
                    "emailAddress": {
                      "address": "jadams@govanguard.com"
                    }
                }
            ],
            "ccRecipients": [
                {
                    "emailAddress": {
                        "address": "jadams@govanguard.com"
                    }
                }
            ]
        },
        "saveToSentItems": "false"
    } 

    # Send get to the appropriate user
    body = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "Text",
                        "content": message 
                    },
                "toRecipients": sendMailHelper(toRecipients), 
                        
                "ccRecipients": sendMailHelper(ccRecipients)
                },
                "saveToSentItems": "false"
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
