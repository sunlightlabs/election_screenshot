from django.shortcuts import render
from screenshotter.models import ElectionUrl

def state_index(request):
    state_groups = ElectionUrl.objects.values('state').distinct()
    states = [grp['state'] for grp in state_groups]
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
