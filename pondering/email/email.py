"""Business logic for creating a phishing campaign narrative."""
# Built-in imports
import logging
import smtplib
import requests
import dns.resolver

# Django framework imports
from django.shortcuts import render

# PyGoPhish imports
from pondering.logginghelper import getClientIp
from pondering.forms import DomainNarrative
from pondering.models import GoPhishing
from pondering.authhelper import AuthHelper
from pondering.graphhelper import getMyMail

# SMTP lib error imports
from smtplib import SMTPConnectError
from smtplib import SMTPHeloError
from smtplib import SMTPNotSupportedError

# DNS resolver error imports
from dns.exception import Timeout
from dns.exception import DNSException
from dns.resolver import NoAnswer

# Django framework error imports
from django.core.exceptions import FieldError
from django.db.utils import IntegrityError


class Email:
    """Phishing narrative class methods."""

    def getEmailContext(context):
        """Email context initializer."""
        context['emailFrom'] = ''
        context['preview'] = ''
        context['subject'] = ''
        context['keyword'] = ''
        context['body'] = ''
        return context

    def postEmailContext(request, context):
        """Email context handler."""
        emailForm = DomainNarrative(request.POST, request.FILES)
        if emailForm.is_valid():
            logging.info("The data provided by {0} to the email formatter is valid.".format(getClientIp(request)))
            data = emailForm.cleaned_data
            emailFrom = data['emailFrom']
            preview = data['preview']
            subject = data['subject']
            keyword = data['keyword']
            body = data['body']
            Email.filterEmailInstance(emailFrom, preview, subject, keyword, body)
            print(data)
            context.update(data)
            return context
        else:
            logging.warning('Client has deliberately circumvented JavaScript input filtering.')
            logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
            return context

    def filterEmailInstance(emailFrom, preview, subject, keyword, body):
        """Email narrative duplication filter."""
        narrative = None
        try:
            narrative = GoPhishing.PhishingEmail.objects.filter(emailFrom__iexact=emailFrom).filter(preview__iexact=preview).filter(subject__iexact=subject).filter(keyword__iexact=keyword).filter(body__iexact=body)
        except FieldError as exc:
            logging.error('No email narratives exist: {0}'.format(exc))
            logging.info('Generating first phishing email narrative: {0},{1}'.format(emailFrom, subject))
            narrative = Email.createEmailInstance(emailFrom, preview, subject, keyword, body)
        else:
            result = narrative.first()
            if result is None:
                narrative = Email.createEmailInstance(emailFrom, preview, subject, keyword, body)
            else:
                narrative = result
        finally:
            narrative.save()
            return narrative

    def createEmailInstance(emailFrom, preview, subject, keyword, body):
        narrative = GoPhishing.PhishingEmail()
        narrative.emailFrom = emailFrom
        narrative.preview = preview
        narrative.subject = subject
        narrative.keyword = keyword
        narrative.body = body
        return narrative

    def generateTestEmailSMTP(request, context):
        emailFrom = context['emailFrom']
        emailTo = context['preview']
        keyword = context['keyword']
        subject = context['subject']
        body = context['body']
        user = context['user']
        domain = emailFrom[emailFrom.find('@')+1:]
        mxservers = []
        connections = []
        connectionReport = {'ConnectionReport': {}}
        # Discover mail exchange servers using the mail exchange record
        try:
            response = dns.resolver.query(domain, 'MX')
        except Timeout as exc:
            logging.error("The DNS request to {0} timed out: {1}".format(domain, exc))
            connectionReport.append(('DNS','Domain name resolution timed out.'))
        except NoAnswer as exc:
            logging.error("The DNS request to {0} failed to resolve: {1}".format(domain, exc))
            connectionReport.append('DNS', 'Domain name server doesn\'t recognize {0}.'.format(domain))
        else:
            for mxserver in response:
                mxservers.append(mxserver.exchange.to_text())
        # Attempt connecting to each mail exchange server
        try:
            for server in mxservers:
                with smtplib.SMTP(server) as smtp:
                    # Store the connection status
                    connectionReport['ConnectionReport']['Connect'] = smtp.connect(server)
                    connectionReport['ConnectionReport']['ESMTP'] = smtp.esmtp_features
                    # Attempt issuing a helo request to the mail exchange server
                    try:
                        # Store the helo response
                        connectionReport['ConnectionReport']['Helo'] = smtp.helo()
                    except SMTPHeloError as exc:
                        # Log and report the helo request failing, if it fails
                        logging.error("The helo request to {0} failed: {1}".format(domain, exc))
                        connectionReport['ConnectionReport']['Helo'] = 'Failed'
                        connectionReport['ConnectionReport']['Helo']['Error'] = exc
                    # Attempt issuing a ehlo request to the mail exchange server
                    try:
                        # Store the helo response
                        connectionReport['ConnectionReport']['Ehlo'] = smtp.ehlo()
                    except SMTPHeloError as exc:
                        # Log and report the helo request failing, if it fails
                        logging.error("The ehlo request to {0} failed: {1}".format(domain, exc))
                        connectionReport['ConnectionReport']['Ehlo'] = 'Failed'
                        connectionReport['ConnectionReport']['Ehlo']['Error'] = exc
                    # Attempt issuing a from request to the mail exchange server
                    try:
                        # Store the Mail From response 
                        connectionReport['ConnectionReport']['From'] = smtp.mail('<{0}>'.format(emailFrom))
                    # Check if SMTP is not supported
                    except SMTPNotSupportedError as exc:
                        # Log and report the mail from request failing, if it fails
                        logging.error("{0} does not support SMTP over http.".format(mxservers[count]))
                        connectionReport['ConnectionReport']['From'] = 'Failed'
                        connectionReport['ConnectionReport']['From']['Error'] = exc
                    # Log and report a value error generated by user input.
                    except ValueError as exc:
                        # Log and report the mail from request failing, if it fails
                        logging.error(exc)
                        connectionReport['ConnectionReport']['From'] = 'Failed'
                        connectionReport['ConnectionReport']['From']['Error'] = exc
                    # Attempt issuing a to request to the mail exchange server
                    try:
                        # Store the Rcpt To response
                        connectionReport['ConnectionReport']['To'] = smtp.rcpt(emailTo)
                    # Log and report a value error generated by user input.
                    except ValueError as exc:
                        # Log and report the mail to request failing, if it fails
                        logging.error(exc)
                        connectionReport['ConnectionReport']['To'] = 'Failed'
                        connectionReport['ConnectionReport']['To']['Error'] = exc
                    # Attempt issuing a message body request to the mail exchange server
                    try:
                        # Store the message body response
                        connectionReport['ConnectionReport']['Body'] = smtp.data(body)
                    except ValueError as exc:
                        logging.error(exc)
                        connectionReport['ConnectionReport']['Body']['Error'] = exc
        except SMTPConnectError as exc:
            logging.error("{0} did not respond to an SMTP connection request and generated the following error: ".format(domain, exc))
            connectionReport['ConnectionReport']['Connect'] = 'Ignored/Timed Out'
            connectionReport['ConnectionReport']['Connect']['Error'] = exc
        except ConnectionRefusedError as exc:
            logging.error("{0} refused an SMTP connection request and generated the following error:".format(domain, exc))
            connectionReport['ConnectionReport']['Connect'] = 'Refused'
            connectionReport['ConnectionReport']['Connect']['Error'] = exc
        context.update(connectionReport)
        print(context)
        return render(request, 'pondering/test.html', context=context)

    def generateTestEmailGraph(request, context):
        connectionReport = {'ConnectionReport': {}}
        token = AuthHelper.getToken(request)
        try:
            email = getMyMail(token)
        except ConnectionError:
            logging.error("{0} did not allow a connection using {1}'s account and produced the following error: {3}".format('Microsoft Graph', context['user'], exc))
        else:
            connectionReport['ConnectionReport'] = {'Microsoft Graph': email}
        context.update(connectionReport)
        return render(request, 'pondering/test.html', context=context)

    def generateTestEmailO365(request, context):
        token = AuthHelper.getToken(request)
        try:
            email = getMyMail(token)
        except ConnectionError:
            logging.error("{0} did not allow a connection using {1}'s account and produced the following error: {3}".format('Microsoft Graph', context['user'], exc))
        else:
            connectionReport['connectionReport'] = {'Microsoft Graph: ', email}
        context.update(connectionReport)
        return render(request, 'pondering/test.html', context=context)

