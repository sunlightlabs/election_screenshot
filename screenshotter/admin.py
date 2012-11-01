from django.contrib import admin
from screenshotter.models import ElectionUrl, ElectionScreenshot


admin.site.register(ElectionUrl)
admin.site.register(ElectionScreenshot)

