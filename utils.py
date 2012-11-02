import logbook

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


