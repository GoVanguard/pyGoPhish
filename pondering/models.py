import uuid 
from django.db import models
from django.urls import reverse


class PointOfContact(models.Model):
    """Model for organizing points of contact for information concerning a specific company."""
    name = models.CharField(max_length=32, null=True, blank=True, help_text='Point of contact that knows the most about a specific company.')

    def __str__(self):
        """Point of contact object string."""
        return self.name


class Company(models.Model):
    """Model for organizing companies that are contracting social engineering."""
    name = models.CharField(max_length=32, null=True, blank=True, help_text='Company that contracted GoVanguard for a phishing campaign.')
    poc = models.ForeignKey('pointofcontact', on_delete=models.RESTRICT, null=True, help_text='Point of contact within GoVanguard that knows the most about a specific company.')

    def getCompany(self):
        """Retrieves the company string."""
        return self.name

    def getPointOfContact(self):
        """Retrieves the point of contact string."""
        return self.poc.name

    def getCompaniesByPOC(self, name):
        """Retrieves the companies listed underneath a specific point of contact."""
        result = None
        try:
            result = Company.objects.filter(poc__name__icontains=name)
        except FieldError as exc:
            logging.error('No points of contact exist: {0}'.format(exc))
        finally:
            return result 

    def __str__(self):
        """Company object string."""
        return "{0},{1}".format(self.name,self.poc)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"


class Owner(models.Model):
    """Model for organizing social engineering campaign owners."""
    name = models.CharField(max_length=32, null=True, blank=True, help_text='Owner of the social engineering campaign the company is contracting with GoVanguard.')

    def getOwner(self):
        """Retrieves the owner string."""
        return self.__str__()

    def __str__(self):
        """Returns the owner string."""
        return self.name


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


class CompanyProfile(models.Model):
    """Model for storing information related to the target company."""
    liname = models.CharField(max_length=200, help_text='The registered company name with LinkedIn.')


class PhishingTrip(models.Model):
    """Model for scheduling phishing trips."""
    company = models.ForeignKey('company', on_delete=models.RESTRICT, null=True, help_text='Company contracting the social engineering campaign from GoVanguard.')
    owner = models.ForeignKey('owner', on_delete=models.RESTRICT, null=True, help_text='Owner of the social engineering campaign the company is contracting with GoVanguard.')

    def getCompany(self):
        """Retrieves the embedded company name."""
        return self.company.getCompany()

    def getOwner(self):
        """Retrieves the embedded owner name."""
        return self.owner.getOwner()

    def __str__(self):
        """Phishing trip object string."""
        return "{0}, {1}".format(self.company, self.owner)


class TargetEmailAddress(models.Model):
    """Model for storing a target e-mail address."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), help_text='Unique ID for this particular e-mail address.')
    email = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you are sending an e-mali to.')

    def getEmail(self):
        """Retrieves the target e-mail string."""
        return self.email


class PhishingList(models.Model):
    """Model for collecting a list of target e-mail addresses."""
    phishingList = models.ForeignKey('targetemailaddress', on_delete=models.RESTRICT, null=True, help_text='List of potential e-mail addresses.')


class PhishingEmail(models.Model):
    """Model for drafting phishing emails."""
    SMTP = 'SMTP'
    MICROSOFT_GRAPH = 'GRPH'
    OFFICE_365 = 'O365'
    SERVICE_CHOICES = [
        (SMTP, 'Simple Mail Transfer Protocol'),
        (MICROSOFT_GRAPH, 'Microsoft Graph'),
        (OFFICE_365, 'Microsoft Office 365'),
    ]
    service = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        help_text='Service providing the mail exchange server.'
    )
    LINKED_IN = 'LI2U'
    GRAPH_IO = 'GRIO'
    GOVANGUARD = 'GOVD'
    ENUMERATION_CHOICES = [
        (LINKED_IN, 'LinkedIn2Username'),
        (GRAPH_IO, 'Graph IO'),
        (GOVANGUARD, 'GoVanguard Email Enumeration'),
    ]
    enumeration = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        help_text='Service providing the email enumeration service.'
    )
    domain = models.URLField(max_length=2048, null=True, blank=True, help_text='The location to launch a phishing campaign from.')
    efrom = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you are sending an e-mail from.')
    to = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you want to preview the e-mail in.')
    subject = models.CharField(max_length=998, null=True, blank=True, help_text='The subject for the phishing campaign e-mail.')
    keyword = models.CharField(max_length=20, null=True, blank=True, help_text='The template keyword used to substitute in the phishing domain.')
    body = models.CharField(max_length=10000, null=True, blank=True, help_text='The body of the phishing campaign e-mail.')


class PhishingTripInstance(models.Model):
    """Model representing a specific phishing trip event."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), help_text='Unique ID for this particular phishing trip.')
    trip = models.ForeignKey('phishingtrip', on_delete=models.RESTRICT, null=True, help_text='Create a phishing trip, which may include multiple domains.')
    pond = models.OneToOneField(PhishingWebsite, on_delete=models.CASCADE, null=True, help_text='The phishing website.')
    target = models.OneToOneField(TargetWebsite, on_delete=models.CASCADE, null=True, help_text='The client website that actively hosts a Simple Mail Transfer Protocol (SMTP) service.')
    email = models.ForeignKey('phishingemail', on_delete=models.CASCADE, null=True, help_text='The phishing e-mail to be used during this campaign.')
    pList = models.ForeignKey('phishinglist', on_delete=models.CASCADE, null=True, help_text='List of potential e-mail addresses.') 
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
        ('a', 'Awaiting Approval'),
        ('i', 'Initializing'),
        ('r', 'Ready'),
        ('p', 'Phishing'),
        ('c', 'Complete'),
        ('e', 'Error'),
    )

    operationalStatus = models.CharField(
        max_length=1,
        choices=OPERATIONAL_STATUS,
        blank=True,
        default='a',
        help_text='Phishing campaign operational status.'
    )

    def getSchedulingStatus(self):
        for count, val in enumerate(self.SCHEDULING_STATUS):
            if val[0] == self.schedulingStatus:
                return val[1]

    def getOperationalStatus(self):
        for count, val in enumerate(self.OPERATIONAL_STATUS):
            if val[0] == self.operationalStatus:
                return val[1]
    
    class Meta:
        ordering = ['datetime'] 

    def __str__(self):
        """String representing this instance."""
        return "{0}, {1}, {2}".format(self.trip.__str__(), self.target, self.datetime)

    def getAbsoluteURL(self):
        """Returns the URL to access phishing trip details."""
        return 'settings/{0}'.format(self.id)
