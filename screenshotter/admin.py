from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from screenshotter.models import ElectionUrl, ElectionScreenshot, ElectionMirror

class ImageWidget(forms.widgets.HiddenInput):
    def render(self, name, value, attrs=None):
        attr_str = u" ".join([u'{k}="{v}"'.format(k=k, v=v)
                              for (k, v) in attrs.items()])
        hidden_field = super(ImageWidget, self).render(name, value, attrs)
        return mark_safe(hidden_field + u'<img src="{0}" {1}>'.format(value, attr_str))

class ElectionScreenshotAdminForm(forms.ModelForm):
    class Media:
        css = {
            'screen': ('admin/screenshotter.css', )
        }

    class Meta:
        model = ElectionScreenshot
        widgets = {
            'image_url': ImageWidget
        }

    def clean_image_url(self):
        return self.instance.image_url

class ElectionUrlAdmin(admin.ModelAdmin):
    list_display = ('state', 'index_url', 'url', 'url_sha1')
    list_filter = ['state']

admin.site.register(ElectionUrl, ElectionUrlAdmin)

class ElectionScreenshotAdmin(admin.ModelAdmin):
    def image_link(mdl):
        return u'<a href="{0.image_url}">[image]</a>'.format(mdl)
    image_link.allow_tags = True
    list_display = ('election_url', 'timestamp', image_link)
    list_filter = ['election_url__state']
    form = ElectionScreenshotAdminForm

admin.site.register(ElectionScreenshot, ElectionScreenshotAdmin)


class ElectionMirrorAdmin(admin.ModelAdmin):
    list_display = ('election_url', 'timestamp')
admin.site.register(ElectionMirror, ElectionMirrorAdmin)

