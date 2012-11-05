import hashlib
import pytz
from django.db import models
from phantomjs import screenshot_url, upload_image
from utils import abbrev_isoformat
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
        screenshots = self.screenshots.order_by('-timestamp')
        return screenshots[0] if screenshots else None

    def latest_mirror(self):
        timestamps = self.mirrors.order_by('-timestamp')
        return timestamps[0] if timestamps else None

    def __unicode__(self):
        return u"{0.state} {0.url}".format(self)

    def take_screenshot(self):
        """Takes a screenshot and creates a new ElectionScreenshot object.
        Returns either None or the ElectionScreenshot object."""
        local_timezone = pytz.timezone(settings.TIME_ZONE)
        now = pytz.datetime.datetime.now(tz=local_timezone)
        previous = self.latest_screenshot()

        def upload_or_link(tmpfile):
            """This is called from inside screenshot_url to avoid
            uploading duplicate files to S3 when the page has not
            changed."""
            with file(tmpfile) as fil_ro:
                bytes = fil_ro.read()
                image_sha1 = hashlib.sha1(bytes).hexdigest()
                if previous and previous.image_sha1 == image_sha1:
                    return (previous.image_sha1, previous.image_url)
                else:
                    filename = "{hash}/{hash}_{timestamp}.png".format(hash=self.url_sha1,
                                                                      timestamp=abbrev_isoformat(now))
                    new_url = upload_image(tmpfile, filename, 'image/png')
                    if new_url is not None:
                        return None
                    return (image_sha1, new_url)

        screenshot_info = screenshot_url(self.url, upload_or_link)
        if screenshot_info is not None:
            (image_sha1, image_url) = screenshot_info
            screenshot = ElectionScreenshot.objects.create(election_url=self,
                                                           timestamp=now,
                                                           image_url=image_url,
                                                           image_sha1=image_sha1)
            return screenshot
        else:
            return None

class ElectionScreenshot(models.Model):
    election_url = models.ForeignKey(ElectionUrl, related_name='screenshots')
    timestamp = models.DateTimeField()
    image_url = models.URLField(help_text="URL of S3 image")
    image_sha1 = models.CharField(max_length=40, null=True, blank=True)

class ElectionMirror(models.Model):
    election_url = models.ForeignKey(ElectionUrl, related_name='mirrors')
    timestamp = models.DateTimeField()
    dir = models.TextField()

