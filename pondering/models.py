import uuid 
from django.db import models
from django.urls import reverse


# TODO: Refactor class models to reflect database inheritance chain. In reflexive cases order alphabetically.

class PhishingWebsite(models.Model):
    """Model for the location and representation of the phishing website."""
    url = models.URLField(max_length=2048, help_text='The phishing website.')
    hyperlink = models.CharField(max_length=2048, null=True, blank=True, help_text='The hyperlink you want the phishing website to appear as.')

    def getPlainTextURL(self):
        return self.__str__()

    def getHTMLURL(self):
        return self.__repr__()

    def __str__(self):
        """PhishingDomain text string."""
        return self.url

    def __repr__(self):
        """PhishingDomain object string."""
        return '<a href="{0}">{1}</a>'.format(self.url, self.hyperlink) 


class TargetWebsite(models.Model):
    """Model for the target website."""
    url = models.URLField(max_length=2048, help_text='The client website that actively hosts a Simple Mail Transfer Protocol (SMTP) service.')
    
    def __str__(self):
        """Target object string."""
        return self.url

class PointOfContact(models.Model):
    """Model for organizing points of contact for information concerning a specific company."""
    poc = models.CharField(max_length=32, null=True, blank=True, help_text='Point of contact that knows the most about a specific company.')

    def __str__(self):
        """Point of contact object string."""
        return self.poc


class Company(models.Model):
    """Model for organizing companies that are contracting social engineering."""
    company = models.CharField(max_length=32, null=True, blank=True, help_text='Company that contracted GoVanguard for a phishing campaign.')
    poc = models.ForeignKey('pointofcontact', on_delete=models.RESTRICT, null=True, help_text='Point of contact within GoVanguard that knows the most about a specific company.')

    def getCompany(self):
        """Retrieves the company string."""
        return self.company

    def getPointOfContact(self):
        """Retrieves the point of contact string."""
        return self.poc.poc

    def getCompaniesByPOC(self, name):
        return self.objects.filter(poc__poc=name)

    def __str__(self):
        """Company object string."""
        return "{0},{1}".format(self.company,self.poc)


class Owner(models.Model):
    """Model for organizing social engineering campaign owners."""
    owner = models.CharField(max_length=32, null=True, blank=True, help_text='Owner of the social engineering campaign the company is contracting with GoVanguard.')


class PhishingTrip(models.Model):
    """Model for scheduling phishing trips."""
    company = models.ForeignKey('company', on_delete=models.RESTRICT, null=True, help_text='Company contracting the social engineering campaign from GoVanguard.')
    poc = models.ForeignKey('pointofcontact', on_delete=models.RESTRICT, null=True, help_text='Point of contact within GoVanguard that knows the most about a specific company.')

    def __str__(self):
        """Phishing trip object string."""
        return "{0}, {1}".format(self.company, self.poc)


class PhishingEmail(models.Model):
    """Model for drafting phishing emails."""
    targetWebsite = models.ForeignKey('targetwebsite', on_delete=models.RESTRICT, null=True, help_text='Register the URL that actively hosts a Simple Mail Transfer Protocol (SMTP) service.')
    mailTo = models.ForeignKey('targetemail', on_delete=models.RESTRICT, null=True, blank=True, help_text='The e-mail address you are sending an e-mail to.')
    mailFrom = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you are sending an e-mail from.')
    preview = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you want to preview the e-mail in.')
    subject = models.CharField(max_length=998, null=True, blank=True, help_text='The subject for the phishing campaign e-mail.')
    body = models.CharField(max_length=10000, null=True, blank=True, help_text='The body of the phishing campaign e-mail.')
    keyword = models.CharField(max_length=20, null=True, blank=True, help_text='The template keyword used to substitute in the phishing domain.')


class TargetEmail(models.Model):
    """Model for storing a target email address."""
    email = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you are sending an e-mali to.')


class PhishingList(models.Model):
    """Model for collecting a list of target email addresses."""
    phishingList = models.ForeignKey('targetemail', on_delete=models.RESTRICT, null=True, help_text='Hyperlink representation of the phishing domain.')


class PhishingTripInstance(models.Model):
    """Model representing a specific phishing trip event."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular phishing trip.')
    owner = models.ForeignKey('owner', on_delete=models.RESTRICT, null=True, help_text='Owner of the social engineering campaign the company is contracting with GoVanguard.')
    trip = models.ForeignKey('phishingtrip', on_delete=models.RESTRICT, null=True, help_text='Create a phishing trip, which may include multiple domains.')
    pond = models.OneToOneField(PhishingWebsite, on_delete=models.CASCADE, null=True, help_text='The phishing website.')
    target = models.OneToOneField(TargetWebsite, on_delete=models.CASCADE, null=True, help_text='The client website that actively hosts a Simple Mail Transfer Protocol (SMTP) service.')
    datetime = models.DateTimeField(max_length=20)

    SCHEDULING_STATUS = (
        ('p', 'Pending'),
        ('s', 'Signed'),
        ('a', 'Approved'),
    )

    schedulingStatus = models.CharField(
        max_length=1,
        choices=SCHEDULING_STATUS,
        blank=True,
        default='p',
        help_text='Phishing campaign contract status.',
    )

    OPERATIONAL_STATUS = (
        ('i', 'Initializing'),
        ('r', 'Ready'),
        ('p', 'Phishing'),
        ('c', 'Complete'),
        ('e', 'Error'),
    )

    operationalSatus = models.CharField(
        max_length=1,
        choices=OPERATIONAL_STATUS,
        blank=True,
        default='p',
        help_text='Phishing campaign operational status.'
    )

    class Meta:
        ordering = ['datetime'] 

    def __str__(self):
        """String representing this instance."""
        return "{0}, {1}, {2}".format(self.trip.__str__(), self.target, self.datetime)

    def getAbsoluteURL(self):
        """Returns the URL to access phishing trip details."""
        return 'schedule/{0}'.format(self.id)


class PhishingResult(models.Model): 
    """Model for collecting results from a phishing trip instance."""
    result = models.ForeignKey('phishingtripinstance', on_delete=models.RESTRICT, null=True, help_text='An individual phishing campaign.')
    phishingList = models.ForeignKey('phishinglist', on_delete=models.RESTRICT, null=True, help_text='List of e-mail addresses for this phishing campaign.')
    phishingEmail = models.ForeignKey('phishingemail', on_delete=models.RESTRICT, null=True, help_text='The e-mail template for this phishing campaign.')
