import os
import sys
import re
import subprocess
from tempfile import NamedTemporaryFile

import logbook
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from utils import run_subprocess_safely, ProcessTimeout

from django.conf import settings


_script_ = (os.path.basename(__file__)
            if __name__ == "__main__"
            else __name__)
log = logbook.Logger(_script_)


def ensure_phantomjs_is_runnable():
    """
    phantomjs must be on the PATH environment variable. This
    tries to run it and log the version, raising an error if
    it fails.
    """
    try:
        process = subprocess.Popen(args=['phantomjs', '--version'],
                                   stdin=None,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except OSError as e:
        if e.errno == 2: # No such file or directory
            log.critical("Unable to find phantomjs")
            sys.exit(1)

    process.wait()
    stdout = process.stdout.read()
    stderr = process.stderr.read()

    if process.returncode != 0:
        log.critical("Unable to execute phantomjs --version: {stdout!r} {stderr!r}",
                     stdout=stdout, stderr=stderr)
        sys.exit(1)

    match = re.match('^\d+\.\d+\.\d+$', stdout.strip())
    if match is None:
        log.critical("Unrecognized version of phantomjs: {stdout!r}", stdout)
        sys.exit(1)

    log.notice("Found phantomjs version {version}", version=match.group())


def screenshot_url(url, callback):
    with NamedTemporaryFile(mode='wb', prefix='twoops', suffix='.png', delete=True) as fil:
        try:
            cmd = ["phantomjs", "rasterize.js", url, fil.name]
            (stdout, stderr) = run_subprocess_safely(cmd,
                                                     timeout=30,
                                                     timeout_signal=15)
            return callback(fil.name)
        except ProcessTimeout as e:
            log.warning(u"PhantomJS timed out on {0}: {1}".format(url, unicode(e)))
            return None

def upload_image(tmp_path, dest_filename, content_type):
    bucket_name = settings.AWS_BUCKET_NAME
    access_key = settings.AWS_ACCESS_KEY
    secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    url_prefix = settings.AWS_URL_PREFIX

    dest_path = os.path.join(url_prefix, dest_filename)
    url = 'http://s3.amazonaws.com/%s/%s' % (bucket_name, dest_path)

    conn = S3Connection(access_key, secret_access_key)
    bucket = conn.create_bucket(bucket_name)
    key = Key(bucket)
    key.key = dest_path
    try:
        key.set_contents_from_filename(tmp_path,
                                       policy='public-read',
                                       headers={'Content-Type': content_type})
        log.notice("Uploaded image {0} to {1}", tmp_path, url)
        return url
    except IOError as e:
        log.warn("Failed to upload image {0} to {1} because {2}", tmp_path, url, str(e))
        return None
