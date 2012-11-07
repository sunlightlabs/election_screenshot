from operator import itemgetter
from django.shortcuts import render
from django.db.models import Max
from screenshotter.models import ElectionUrl, ElectionMirror, ElectionScreenshot

def state_index(request):
    state_groups = ElectionUrl.objects.values('state').distinct()
    state_lookup = dict(((grp['state'], grp) for grp in state_groups))
    latest_screenshots = ElectionScreenshot.objects.values('election_url__state').annotate(timestamp=Max('timestamp'))
    for screenshot in latest_screenshots:
        state_lookup[screenshot['election_url__state']]['latest_screenshot'] = screenshot['timestamp']
    latest_mirrors = ElectionMirror.objects.values('election_url__state').annotate(timestamp=Max('timestamp'))
    for mirror in latest_mirrors:
        state_lookup[mirror['election_url__state']]['latest_mirror'] = mirror['timestamp']
    
    states = list(state_lookup.items())
    states.sort(key=itemgetter(0))

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
