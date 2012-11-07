import sys
import time
import threading
import os
import subprocess
import logbook
import django.db


_script_ = (os.path.basename(__file__)
            if __name__ == "__main__"
            else __name__)
log = logbook.Logger(_script_)


class ProcessTimeout(Exception):
    def __init__(self, cmd, process, stdout, stderr, *args, **kwargs):
        msg = u"Process timeout for pid {process.pid}; cmd: {cmd!r} stdout: {stdout!r}, stderr: {stderr!r}".format(process=process, cmd=cmd, stdout=stdout, stderr=stderr)
        super(ProcessTimeout, self).__init__(msg, *args, **kwargs)
        self.cmd = cmd
        self.process = process


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
        raise ProcessTimeout(args, process, stdout, stderr)
    else:
        deadline_timer.cancel()
        log.notice(u"Process completed in {0} seconds with return code {1}: {2} (stdout: {3!r}) (stderr: {4!r})", elapsed, process.returncode, args, stdout, stderr)
        return (stdout, stderr)

def configure_log_handler(application_name, loglevel, output):
    if isinstance(loglevel, (str, unicode)):
        loglevel = getattr(logbook, loglevel.upper())

    if not isinstance(loglevel, int):
        raise TypeError("configure_log_handler expects loglevel to be either an integer or a string corresponding to an integer attribute of the logbook module.")

    if output == 'syslog':
        log_handler = logbook.SyslogHandler(
            application_name=application_name,
            facility='user',
            bubble=False,
            level=loglevel)
    elif output == '-' or not output:
        log_handler = logbook.StderrHandler(
            level=loglevel,
            bubble=False)
    else:
        log_handler = logbook.FileHandler(
            filename=output,
            encoding='utf-8',
            level=loglevel,
            bubble=False)

    return log_handler


def restart_process():
    """
    Replaces the current process with a new process invoked
    using the same command line.
    """
    try:
        django.db.close_connection()
    except Exception as e:
        log.warning("While trying to close database connection before restart: {e}", e=unicode(e))
    except:
        pass
        
    os.execl(sys.executable, sys.executable, *sys.argv)


def abbrev_isoformat(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")

