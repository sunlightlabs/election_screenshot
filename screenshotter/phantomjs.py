import os
import sys
import time
import threading
import re
import subprocess
import datetime
import hashlib
from tempfile import NamedTemporaryFile

import logbook
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.conf import settings


_script_ = (os.path.basename(__file__)
            if __name__ == "__main__"
            else __name__)
log = logbook.Logger(_script_)


class PhantomJSTimeout(Exception):
    def __init__(self, cmd, process, stdout, stderr, *args, **kwargs):
        msg = u"phantomjs timeout for pid {process.pid}; cmd: {cmd!r} stdout: {stdout!r}, stderr: {stderr!r}".format(process=process, cmd=cmd, stdout=stdout, stderr=stderr)
        super(PhantomJSTimeout, self).__init__(msg, *args, **kwargs)
        self.cmd = cmd
        self.process = process


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


def run_subprocess_safely(args, timeout=300, timeout_signal=9):
    """
    args: sequence of args, see Popen docs for shell=False
    timeout: maximum runtime in seconds (fractional seconds allowed)
    timeout_signal: signal to send to the process if timeout elapses
    """
    log.debug(u"Starting command: {0}", args)

    process = subprocess.Popen(args=args,
                               stdin=None,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    deadline_timer = threading.Timer(timeout, process.send_signal, args=(timeout_signal,))
    deadline_timer.start()

    stdout = ""
    stderr = ""
    start_time = time.time()
    elapsed = 0

    # In practice process.communicate() never seems to return
    # until the process exits but the documentation implies that
    # it can because EOF can be reached before the process exits.
    while not timeout or elapsed < timeout:
        (stdout1, stderr1) = process.communicate()
        if stdout1:
            stdout += stdout1
        if stderr1:
            stderr += stderr1
        elapsed = time.time() - start_time
        if process.poll() is not None:
            break

    if elapsed >= timeout:
        log.warning(u"Process failed to complete within {0} seconds. Return code: {1}", timeout, process.returncode)
        raise PhantomJSTimeout(args, process, stdout, stderr)
    else:
        deadline_timer.cancel()
        log.notice(u"Process completed in {0} seconds with return code {1}: {2} (stdout: {3!r}) (stderr: {4!r})", elapsed, process.returncode, args, stdout, stderr)
        return (stdout, stderr)


def screenshot_url(url):
    now = datetime.datetime.now().isoformat()
    sha1 = hashlib.sha1(url).hexdigest()
    filename = "{hash}-{timestamp}.png".format(hash=sha1, timestamp=now)

    with NamedTemporaryFile(mode='wb', prefix='twoops', suffix='.png', delete=True) as fil:
        cmd = ["phantomjs", "rasterize.js", url, fil.name]
        (stdout, stderr) = run_subprocess_safely(cmd,
                                                 timeout=30,
                                                 timeout_signal=15)
        new_url = upload_image(fil.name, filename, 'image/png')
        return new_url

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
