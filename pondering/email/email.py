"""Business logic for creating a phishing campaign narrative."""
# Built-in imports
import logging
import requests
import uuid
import smtplib
import json
from email import message

# SMTP lib error imports
from smtplib import SMTPConnectError
from smtplib import SMTPHeloError
from smtplib import SMTPNotSupportedError
from smtplib import SMTPDataError

# Requests library imports
import requests

# Django framework imports
from django.shortcuts import render
from django.http import HttpResponseRedirect

# Django framework error imports
from django.core.exceptions import FieldError
from django.db.utils import IntegrityError

# Dnspython imports
import dns.resolver

# DNS resolver error imports
from dns.exception import Timeout
from dns.exception import DNSException
from dns.resolver import NoAnswer

# Office 365 imports
from O365 import Account

# LinkedIn2Username imports
from pondering.LiIn2User import linkedin2username

# PyGoPhish imports
from pondering import models
from pondering.logginghelper import getClientIp
from pondering.forms import DomainNarrative
from pondering import authhelper
from pondering.graphhelper import sendMail


def getEmailContext(request, context):
    """Email GET context handler."""
    instance = request.GET.get('id')
    if instance:
        if uuid.UUID(instance, version=4):
            context['phishingTrip'] = instance
        else:
            logging.warning('Client is attempting parameter fuzzing.')
    return context


def postEmailContext(request, context):
    """Email POST context handler."""
    emailForm = DomainNarrative(request.POST, request.FILES)
    if emailForm.is_valid():
        logging.info("The data provided by {0} to the email formatter is valid.".format(getClientIp(request)))
        data = emailForm.cleaned_data
        instance = data['phishingtrip']
        service = data['service']
        enumeration = data['enumeration']
        domain = data['domain']
        to = data['to']
        cc = data['cc']
        efrom = data['efrom']
        subject = data['subject']
        keyword = data['keyword']
        attachment = data['attachment']
        body = data['body']
        filterEmailInstance(instance, service, enumeration, domain, efrom, to, subject, keyword, attachment, body)
        update = {'Instance': instance, 'Service': service, 'Enumeration': enumeration, 'Domain': domain,
                'From': efrom, 'To': to, 'Cc': cc, 'Subject': subject, 'Keyword': keyword, 'Attachment': attachment, 
                'Body': body}
        context.update(update)
        return context
    else:
        if emailForm.errors:
            logging.error(emailForm.errors)
        logging.warning('Client has deliberately circumvented JavaScript input filtering.')
        logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
        return context


def filterEmailInstance(instance, service, enumeration, domain, efrom, to, subject, keyword, attachment, body):
    """Email narrative duplication filter."""
    narrative = None
    try:
        narrative = models.PhishingEmail.objects.filter(domain__iexact=domain).filter(efrom__iexact=efrom).filter(to__iexact=to).filter(subject__iexact=subject).filter(keyword__iexact=keyword).filter(body__iexact=body)
    except FieldError as exc:
        logging.error('No email narratives exist: {0}'.format(exc))
        logging.info('Generating first phishing email narrative: {0},{1}'.format(efrom, subject))
        narrative = createEmailInstance(service, enumeration, domain, efrom, to, subject, keyword, attachment, body)
    else:
        result = narrative.first()
        if result is None:
            narrative = createEmailInstance(service, enumeration, domain, efrom, to, subject, keyword, attachment, body)
        else:
            narrative = result
    finally:
        narrative.save()
    phishingTrip = None
    try:
        phishingTrip = models.PhishingTripInstance.objects.filter(pk=instance)
    except FieldError as exc:
        # This should never get triggered.
        # The information required to create this object does not exist within this context.
        logging.error('No phishing trips exist: {0}'.format(exc))
        logging.info('Client constructed PyGoPhish, skipped creating a plan, and attempted constructing an e-mail with a properly formatted uuid4 or replaced the uuid4 with one generated by the client.'.format(instance))
    else:
        result = phishingTrip.first()
        if result is not None:
            result.email = narrative
            result.save()


def filterEmailList(emailList):
    """E-mail address duplication filter."""
    for email in emailList:
        target = None
        try:
            target = models.TargetEmailAddress.objects.filter(email__iexact=email)
        except FieldError as exc:
            logging.error('No phishing emails exist: {0}'.format(exc))
            logging.info('Generating first phishing email instance: {0}'.format(email))
            target = createEmail(email)
        else:
            result = target.first()
            if result is None:
                target = createEmail(email)
            else:
                target = result
        finally:
            target.save()


def createEmail(email):
    """This method creates an e-mail address in the sqlite database."""
    target = models.TargetEmailAddress()
    target.id = uuid.uuid4()
    target.email = email
    return target


def createEmailInstance(service, enumeration, domain, efrom, to, subject, keyword, attachment, body):
    """This method creates a phishing narrative in the sqlite database."""
    narrative = models.PhishingEmail()
    narrative.service = service
    narrative.enumeration = enumeration
    narrative.domain = domain
    narrative.efrom = efrom
    narrative.to = to
    narrative.subject = subject
    narrative.keyword = keyword
    narrative.body = body
    narrative.attachment = attachment
    return narrative


def emailSMTP(request, context):
    """This method sends an e-mail using SMTP."""
    efrom = context['From']
    if context['Domain']:
        domain = context['Domain']
    else:
        domain = efrom[efrom.find('@')+1:]
        context['Domain'] = domain
    to = context['To']
    subject = context['Subject']
    keyword = context['Keyword']
    body = context['Body']
    user = context['user']
    mxservers = []
    serverNames = []
    connections = []
    connectionReport = {} 
    serverReport = {}
    # Discover mail exchange servers using the mail exchange record
    try:
        response = dns.resolver.resolve(domain, 'MX')
    except Timeout as exc:
        logging.error("The DNS request to {0} timed out: {1}".format(domain, exc))
        serverReport['DNS'] = 'Failed'
        serverReport['DNS']['Error'] = 'Domain name resolution timed out for {0}.'.format(domain)
        connectionReport.append(serverReport)
    except NoAnswer as exc:
        logging.error("The DNS request to {0} failed to resolve: {1}".format(domain, exc))
        serverReport['DNS'] = 'Failed'
        serverReport['DNS']['Error'] = "Domain name server doesn't recognize {0}.".format(domain)
        connectionReport.append(serverReport)
    else:
        for mxserver in response:
            mxservers.append(mxserver.exchange.to_text())
            serverNames.append(str(mxserver))
        # Attempt connecting to each mail exchange server
        try:
            for count, server in enumerate(mxservers):
                serverReport['Name'] = server
                with smtplib.SMTP(server) as smtp:
                    # Store the connection status
                    serverReport['Connect'] = smtp.connect(server)
                    serverReport['ESMTP'] = smtp.esmtp_features
                    # Attempt issuing a helo request to the mail exchange server
                    try:
                        # Store the helo response
                        serverReport['Helo'] = smtp.helo()
                    except SMTPHeloError as exc:
                        # Log and report the helo request failing, if it fails
                        logging.error("The helo request to {0} failed: {1}".format(domain, exc))
                        serverReport['Helo'] = 'Failed'
                        serverReport['Helo']['Error'] = exc
                    # Attempt issuing a ehlo request to the mail exchange server
                    try:
                        # Store the helo response
                        serverReport['Ehlo'] = smtp.ehlo()
                    except SMTPHeloError as exc:
                        # Log and report the helo request failing, if it fails
                        logging.error("The ehlo request to {0} failed: {1}".format(domain, exc))
                        serverReport['Ehlo'] = 'Failed'
                        serverReport['Ehlo']['Error'] = exc
                    # Attempt issuing a from request to the mail exchange server
                    try:
                        # Store the Mail From response 
                        serverReport['From'] = smtp.mail('<{0}>'.format(efrom))
                    # Check if SMTP is not supported
                    except SMTPNotSupportedError as exc:
                        # Log and report the mail from request failing, if it fails
                        logging.error("{0} does not support SMTP over http.".format(mxservers[count]))
                        serverReport['From'] = 'Failed'
                        serverReport['From']['Error'] = exc
                    # Log and report a value error generated by user input.
                    except ValueError as exc:
                        # Log and report the mail from request failing, if it fails
                        logging.error(exc)
                        serverReport['From'] = 'Failed'
                        serverReport['From']['Error'] = exc
                    # Attempt issuing a to request to the mail exchange server
                    try:
                        # Store the Rcpt To response
                        serverReport['To'] = smtp.rcpt(to)
                    # Log and report a value error generated by user input.
                    except ValueError as exc:
                        # Log and report the mail to request failing, if it fails
                        logging.error(exc)
                        serverReport['To'] = 'Failed'
                        serverReport['To']['Error'] = exc
                    # Attempt closing the session before creating a message
                    try:
                        # Store the quit response
                        serverReport['Quit'] = smtp.quit()
                    # Log and report a session that does not quit
                    except SMTPException as exc:
                        # Log and report the computer failing to quit an smtp session (highly unlikely)
                        logging.error(exc)
                        serverReport['Quit'] = 'Failed'
                        serverReport['Quit']['Error'] = exc
                    # Most people are going to want a modern e-mail format for their messages
                    try:
                        # Store the message body response
                        serverReport['Body'] = smtp.data('\nSubject:{0}\nX-MSMail-Priority: High\nReturn-Receipt-To: {1}\n\n{2}'.format(subject, efrom, body))
                    except ValueError as exc:
                        logging.error(exc)
                        serverReport['Body']['Error'] = exc
                    except SMTPDataError as exc:
                        logging.error(exc)
                        if exc.smtp_code == 503 and emailFrom[emailFrom.find('@')+1:] != domain:
                            serverReport['Body'] = 'The domain used for the from e-mail address is not allowed on {0}.'.format(server)
                            serverReport['Body']['Error'] = exc
                        if exc.smtp_code == 550:
                            serverReport['Body'] = '' 
                            serverReport['Body']['Error'] = exc
                connectionReport[serverNames[count]] = serverReport
        except SMTPConnectError as exc:
            logging.error("{0} did not respond to an SMTP connection request and generated the following error: ".format(domain, exc))
            serverReport['Connect'] = 'Ignored/Timed Out'
            serverReport['Connect']['Error'] = exc
        except ConnectionRefusedError as exc:
            logging.error("{0} refused an SMTP connection request and generated the following error:".format(domain, exc))
            serverReport['Connect'] = 'Refused'
            serverReport['Connect']['Error'] = exc
    finally:
        context.update({'report': connectionReport})
        return context 


def emailGRPH(request, context):
    """This method sends an email with Microsoft Graph."""
    # Create an email object
    # https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0&tabs=csharp
    token = authhelper.getToken(request)
    instance = context['Instance']
    phishingTrip = models.PhishingTripInstance.objects.filter(id=instance)[0]
    hyperlink = phishingTrip.pond.getHTMLURL()
    efrom = context['From']
    to = context['To']
    cc = context['Cc']
    subject = context['Subject']
    keyword = context['Keyword']
    attachement = context['Attachment']
    body = context['Body']
    user = context['user']
    message = {
        "message": {
            "subject": subject,
            "ccRecipients": [
                {
                    "emailAddress": {
                        "address": cc
                    }
                }
            ],
            "isReadReceiptRequested": True,
            "isDraft": True,
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to
                    }
                }
            ],
            "body": {
                "contentType": "HTML",
                "content": "<html>\r\n<head>\r\n<meta http-equiv=\"Content-Type\" content=\"text/html' charset=utf-8\">\r\n<meta content=\"text/html; charset=us-ascii\">\r\n</head>\r\n<body>\r\n{0}\r\n</body>\r\n</html>\r\n".format(body.replace(keyword, hyperlink)),
            },
        }
    }
    response = sendMail(token, json.dumps(message))
    print(response)
    return context 


def emailO365(request, context):
    """This method sends an email with Office 365."""
    return context 


def testMail(acc):
    mailbox = acc.mailbox()
    message = mailbox.new_message()
    message.to.add(['jadams@govanguard.com'])
    message.body = 'Click this link sucker!'
    message.subject = '1 Free Internet'
    message.sender.address = 'Jtest2@quick-books-online.com'
    message.send()
    try:
        email = getMyMail(token)
    except ConnectionError:
        logging.error("{0} did not allow a connection using {1}'s account and produced the following error: {3}".format('Microsoft Graph', context['user'], exc))
    else:
        connectionReport['connectionReport'] = {'Microsoft Graph: ', email}
    context.update(connectionReport)
    return render(request, 'pondering/test.html', context=context)


def authenticate(creds):
    account = Account(creds)
    if account.authenticate(scopes=['basic', 'message_all', 'message_all_shared']):
        return account
