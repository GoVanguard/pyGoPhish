import uuid 
from django.db import models
from django.urls import reverse

class Domain(models.Model):
    url = models.URLField(help_text='Enter a URL.')
    
    def __str__(self):
        """Domain object string."""
        return self.url


class PhishingTrip(models.Model):
    """A simple class for scheduling phishing trips."""
    company = models.CharField(max_length=32, null=True, blank=True, help_text='Company that contracted GoVanguard for a phishing campaign.')
    poc = models.CharField(max_length=32, null=True, blank=True, help_text='GoVanguard employee authorizing the phishing campaign.')

    def __str__(self):
        """Phishing trip object string."""
        return "{0}, {1}".format(self.company, self.poc)


class PhishingTripInstance(models.Model):
    """Model representing a specific phishing trip event."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular phishing trip.')
    trip = models.ForeignKey('PhishingTrip', on_delete=models.RESTRICT, null=True, help_text="Create a phishing trip, which may include multiple domains.")
    domain = models.ForeignKey('Domain', on_delete=models.RESTRICT, null=True, help_text="Register the URL(s) that actively host a Simple Mail Transfer Protocol (SMTP) service.")
    datetime = models.DateTimeField(max_length=20)

    SCHEDULING_STATUS = (
        ('p', 'Pending'),
        ('r', 'Accepted'),
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
        return "{0}, {1}, {2}".format(self.trip.__str__(), self.domain, self.datetime)

    def getAbsoluteURL(self):
        """Returns the URL to access phishing trip details."""
        return 'schedule/{0}'.format(self.id)
