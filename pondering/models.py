import uuid 
from django.db import models
from django.urls import reverse


class PhishingDomain(models.Model):
    url = models.CharField(max_length=2048, help_text='The phishing website.')
    hyperlink = models.CharField(max_length=2048, null=True, blank=True, help_text='The hyperlink you want the phishing website to appear as.')

    def __str__(self):
        """PhishingDomain text string."""
        return self.url

    def __repr__(self):
        """PhishingDomain object string."""
        return '<a href="{0}">{1}</a>'.format(self.url, self.hyperlink) 


class Target(models.Model):
    url = models.URLField(max_length=2048, help_text='The client website.')
    
    def __str__(self):
        """Target object string."""
        return self.url


class PhishingTrip(models.Model):
    """A simple class for scheduling phishing trips."""
    company = models.CharField(max_length=32, null=True, blank=True, help_text='Company that contracted GoVanguard for a phishing campaign.')
    poc = models.CharField(max_length=32, null=True, blank=True, help_text='GoVanguard employee authorizing the phishing campaign.')

    def __str__(self):
        """Phishing trip object string."""
        return "{0}, {1}".format(self.company, self.poc)


class PhishingEmail(models.Model):
    """A simple class for drafting phishing emails."""
    target = models.ForeignKey('target', on_delete=models.RESTRICT, null=True, help_text='Register the URL that actively hosts a Simple Mail Transfer Protocol (SMTP) service.')
    phishingDomain = models.ForeignKey('phishingdomain', on_delete=models.RESTRICT, null=True, help_text='Hyperlink representation of the phishing domain.')
    mailFrom = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you are sending an e-mail from.')
    mailTo = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you are sending an e-mail to.')
    preview = models.EmailField(max_length=320, null=True, blank=True, help_text='The e-mail address you want to preview the e-mail in.')
    subject = models.CharField(max_length=998, null=True, blank=True, help_text='The subject for the phishing campaign e-mail.')
    body = models.CharField(max_length=10000, null=True, blank=True, help_text='The body of the phishing campaign e-mail.')
    keyword = models.CharField(max_length=20, null=True, blank=True, help_text='The template keyword used to substitute in the phishing domain.')
    


class PhishingTripInstance(models.Model):
    """Model representing a specific phishing trip event."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular phishing trip.')
    trip = models.ForeignKey('PhishingTrip', on_delete=models.RESTRICT, null=True, help_text="Create a phishing trip, which may include multiple domains.")
    target = models.ForeignKey('Target', on_delete=models.RESTRICT, null=True, help_text="Register the URL(s) that actively hosts a Simple Mail Transfer Protocol (SMTP) service.")
    datetime = models.DateTimeField(max_length=20)

    SCHEDULING_STATUS = (
        ('p', 'Pending'),
        ('s', 'Signed'),
        ('a', 'Approved'),
    )

    status = models.CharField(
        max_length=1,
        choices=SCHEDULING_STATUS,
        blank=True,
        default='p',
        help_text='Phishing campaign status.',
    )

    class Meta:
        ordering = ['datetime'] 

    def __str__(self):
        """String representing this instance."""
        return "{0}, {1}, {2}".format(self.trip.__str__(), self.target, self.datetime)

    def getAbsoluteURL(self):
        """Returns the URL to access phishing trip details."""
        return 'schedule/{0}'.format(self.id)
