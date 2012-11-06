import os
import pytz
from screenshotter.phantomjs import run_subprocess_safely
from screenshotter.models import ElectionMirror
from utils import abbrev_isoformat
from django.conf import settings

def copy_dir(fro, to):
    args = ["cp",
            "-al",
            fro,
            to]
    run_subprocess_safely(args)

def mirror_url(urlobj):
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    now = pytz.datetime.datetime.now(tz=local_timezone)

    url_mirror_root = os.path.abspath(os.path.join(settings.MIRROR_ROOT,
                                                   urlobj.state,
                                                   urlobj.url_sha1))
    if not os.path.exists(url_mirror_root):
        os.makedirs(url_mirror_root)
    dest_dir = os.path.join(url_mirror_root, abbrev_isoformat(now))
    log_path = os.path.join(url_mirror_root, "wget.log")

    previous = urlobj.latest_mirror()
    if previous:
        copy_dir(previous.dir, dest_dir)
    elif not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    user_agent_arg = ("--user-agent='{ua}'".format(ua=urlobj.user_agent)
                      if urlobj.user_agent
                      else "")
    args = ["wget",
            "--no-verbose",
            "-p",
            "--convert-links",
            "--wait=1",
            "-N",
            "--random-wait",
            user_agent_arg,
            "-o",
            log_path,
            "-P",
            dest_dir,
            urlobj.url]
    (stdout, stderr) = run_subprocess_safely(args)

    mirror = ElectionMirror.objects.create(election_url=urlobj,
                                           timestamp=now,
                                           dir=dest_dir)
    return mirror


