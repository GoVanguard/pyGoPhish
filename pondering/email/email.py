"""Business logic for creating a phishing campaign narrative."""
# Built-in imports
import logging
import smtplib
import requests
import dns.resolver
from uuid import UUID

# Django framework imports
from django.shortcuts import render

# Office 365 imports
from O365 import Account

# LinkedIn2Username imports
from pondering.LiIn2User import linkedin2username

# PyGoPhish imports
from pondering.logginghelper import getClientIp
from pondering.forms import DomainNarrative
from pondering.models import GoPhishing
from pondering.authhelper import AuthHelper
from pondering.graphhelper import sendMail, getMyMail

# SMTP lib error imports
from smtplib import SMTPConnectError
from smtplib import SMTPHeloError
from smtplib import SMTPNotSupportedError
from smtplib import SMTPDataError

# DNS resolver error imports
from dns.exception import Timeout
from dns.exception import DNSException
from dns.resolver import NoAnswer

# Django framework error imports
from django.core.exceptions import FieldError
from django.db.utils import IntegrityError


class Email:
    """Phishing narrative class methods."""
    
    def getEmailContext(request, context):
        """Email GET context handler."""
        phishingTrip = request.GET.get('id')
        if UUID(phishingTrip, version=4):
            context['phishingTrip'] = phishingTrip
        else:
            logging.warning('Client is attempting parameter fuzzing.')
        print(context)
        return context


    def postEmailContext(request, context):
        """Email POST context handler."""
        emailForm = DomainNarrative(request.POST, request.FILES)
        if emailForm.is_valid():
            logging.info("The data provided by {0} to the email formatter is valid.".format(getClientIp(request)))
            data = emailForm.cleaned_data
            instance = data['phishingtrip']
            service = data['service']
            domain = data['domain']
            if service == 'GRPH' or 'O365':
                email = context['user']['email']
                domain = email[email.find('@')+1:]
            efrom = data['efrom']
            to = data['to']
            subject = data['subject']
            keyword = data['keyword']
            body = data['body']
            update = {'Instance': instance, 'Service': service, 'Domain': domain, 'From': efrom, 'To': to,
                    'Subject': subject, 'Keyword': keyword, 'Body': body}
            Email.filterEmailInstance(instance, service, domain, efrom, to, subject, keyword, body)
            context.update(update)
            return context
        else:
            if emailForm.errors:
                logging.error(emailForm.errors)
            logging.warning('Client has deliberately circumvented JavaScript input filtering.')
            logging.warning('Client is attempting an injection attack from: {0}'.format(getClientIp(request)))
            return context

    def filterEmailInstance(instance, service, domain, efrom, to, subject, keyword, body):
        """Email narrative duplication filter."""
        narrative = None
        try:
            narrative = GoPhishing.PhishingEmail.objects.filter(domain__iexact=domain).filter(efrom__iexact=efrom).filter(to__iexact=to).filter(subject__iexact=subject).filter(keyword__iexact=keyword).filter(body__iexact=body)
        except FieldError as exc:
            logging.error('No email narratives exist: {0}'.format(exc))
            logging.info('Generating first phishing email narrative: {0},{1}'.format(efrom, subject))
            narrative = Email.createEmailInstance(service, domain, efrom, to, subject, keyword, body)
        else:
            result = narrative.first()
            if result is None:
                narrative = Email.createEmailInstance(service, domain, efrom, to, subject, keyword, body)
            else:
                narrative = result
        finally:
            narrative.save()
        phishingTrip = None
        try:
            phishingTrip = GoPhishing.PhishingTripInstance.objects.filter(pk=instance)
        except FieldError as exc:
            # This should never get triggered.
            logging.error('No phishing trips exist: {0}'.format(exc))
            logging.info('Generating first phishing trip instance: {0},{1}'.format(instance))
        else:
            result = phishingTrip.first()
            if result is None:
                phishingTrip = GoPhishing.PhisingTripInstance()
            else:
                phishingTrip = result
        finally:
            phishingTrip.email = narrative
            phishingTrip.save()


    def createEmailInstance(service, domain, efrom, to, subject, keyword, body):
        narrative = GoPhishing.PhishingEmail()
        narrative.service = service
        narrative.domain = domain
        narrative.efrom = efrom
        narrative.to = to
        narrative.subject = subject
        narrative.keyword = keyword
        narrative.body = body
        return narrative

    def emailSMTP(request, context):
        if context['Domain']:
            domain = context['Domain']
        else:
            domain = efrom[efrom.find('@')+1:]
            context['Domain'] = domain
        efrom = context['From']
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
                        # Attempt issuing a message body request to the mail exchange server
                        try:
                            # Store the message body response
                            serverReport['Body'] = smtp.data(body)
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
            response = render(request, 'pondering/test.html', context=context)
            return response

    def emailGRPH(request, context):
        service = context['Service']
        email = context['user']['email']
        domain = email[email.find('@')+1:]
        efrom = context['From']
        to = context['To']
        keyword = context['Keyword']
        subject = context['Subject']
        body = context['Body']
        user = context['user']
        token = AuthHelper.getToken(request)
        connectionReport = {'ConnectionReport': {}}
        try:
            email = sendMail(token, subject, body, to, efrom)
            print(email)
        except ConnectionError:
            logging.error("{0} did not allow a connection using {1}'s account and produced the following error: {3}".format('Microsoft Graph', context['user'], exc))
            connectionReport['ConnectionReport']['Email'] = 'Failed'
            connectionReport['ConnectionReport']['Email']['Error'] = exc
        else:
            connectionReport['ConnectionReport']['Email'] = {'Microsoft Graph': email}
        context.update(connectionReport)
        return render(request, 'pondering/test.html', context=context)

    def emailO365(request, context):
        service = context['Service']
        domain = context['Domain']
        efrom = context['From']
        if domain:
            domain = context['Domain']
        else:
            domain = emailFrom[emailFrom.find('@')+1:]
        emailTo = context['To']
        keyword = context['Keyword']
        subject = context['Subject']
        body = context['Body']
        user = context['user']
        creds = AuthHelper.getLi2UserCredentials()
        emailList = Email.linkedInEnumerate(creds, 'xn', '@xnlp.com')
        context['emails'] = emailList
        return render(request, 'pondering/test.html', context=context)


    def linkedInEnumerate(creds, company, address):
        emailList = []
        session = linkedin2username.login(creds)
        if not session:
            logging.Error('LinkedIn2Username failed to login with the credentials provided.')
        else:
            session = linkedin2username.set_search_csrf(session)
            companyId, staff_count = linkedin2username.get_company_info(company, session)
            foundNames = linkedin2username.scrape_info(session, companyId, staff_count, creds)
            cleanList = linkedin2username.clean(foundNames)
            emailList = linkedin2username.write_list(company, address, cleanList)
        return emailList


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
