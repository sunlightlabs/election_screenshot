import pytz
import hashlib
from django.db import models
from phantomjs import screenshot_url
from django.conf import settings


class ElectionUrl(models.Model):
    index_url = models.URLField(help_text="URL of the index page for the board of elections")
    url = models.URLField(help_text="url to be screenshotted")
    url_sha1 = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=2, help_text="Two char abbreviation for the state, AL e.g.")

    def save(self, *args, **kwargs):
        self.url_sha1 = hashlib.sha1(self.url).hexdigest()
        super(ElectionUrl, self).save(*args, **kwargs)

    def latest_screenshot(self):
        return self.screenshots.order_by('-timestamp')[0]

    def __unicode__(self):
        return u"{0.state} {0.url}".format(self)

    def take_screenshot(self):
        local_timezone = pytz.timezone(settings.TIME_ZONE)

        new_url = screenshot_url(self.url)
        screenshot = ElectionScreenshot(election_url=self,
                                        timestamp=pytz.datetime.datetime.now(tz=local_timezone),
                                        image_url=new_url)
        screenshot.save()

class ElectionScreenshot(models.Model):
    election_url = models.ForeignKey(ElectionUrl, related_name='screenshots')
    timestamp = models.DateTimeField()
    image_url = models.URLField(help_text="URL of S3 image")
