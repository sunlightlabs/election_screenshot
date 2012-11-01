from django.db import models
from django.contrib import admin

class ElectionUrl(models.Model):
    index_url = models.URLField(help_text="URL of the index page for the board of elections")
    url = models.URLField(help_text="url to be screenshotted")
    state = models.CharField(max_length=2, help_text="Two char abbreviation for the state, AL e.g.")


class ElectionScreenshot(models.Model):
    election_url = models.ForeignKey(ElectionUrl)
    timestamp = models.DateTimeField()
    image_url = models.URLField(help_text="URL of S3 image")


admin.site.register(ElectionUrl)
