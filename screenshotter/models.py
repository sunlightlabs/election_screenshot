from django.db import models


class ElectionUrl(models.Model):
    index_url = models.URLField(help_text="URL of the index page for the board of elections")
    url = models.URLField(help_text="url to be screenshotted")
    state = models.CharField(max_length=2, help_text="Two char abbreviation for the state, AL e.g.")

    def latest_screenshot(self):
        return self.screenshots.order_by('-timestamp')[0]


class ElectionScreenshot(models.Model):
    election_url = models.ForeignKey(ElectionUrl, related_name='screenshots')
    timestamp = models.DateTimeField()
    image_url = models.URLField(help_text="URL of S3 image")

