from django.shortcuts import render
from screenshotter.models import ElectionUrl, ElectionMirror, ElectionScreenshot

def state_index(request):
    state_groups = ElectionUrl.objects.values('state').distinct()
    states = sorted([grp['state'] for grp in state_groups])
    return render(request, "state_index.html", {
        'states': states
    })

def state_details(request, state):
    urls = ElectionUrl.objects.filter(state=state)
    return render(request, "state_details.html", {
        'state': state,
        'urls': urls
    })

def url_details(request, state, sha1):
    url = ElectionUrl.objects.get(state=state, url_sha1=sha1)
    screenshots = url.screenshots.order_by('timestamp')
    mirrors = url.mirrors.order_by('timestamp')
    return render(request, "url_details.html", {
        'state': state,
        'url': url,
        'screenshots': screenshots,
        'mirrors': mirrors
    })


def point_in_time(request, sha1, timestamp):
    pass

def status(request):
    mirrors = ElectionMirror.objects.order_by('-timestamp')
    screenshots = ElectionScreenshot.objects.order_by('-timestamp')

    latest_mirror = None if mirrors.count() == 0 else mirrors[0]
    latest_screenshot = None if screenshots.count() == 0 else screenshots[0]

    return render(request, 'status.html', {
        'latest_mirror': latest_mirror,
        'latest_screenshot': latest_screenshot
    })
