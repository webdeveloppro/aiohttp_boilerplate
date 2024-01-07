import logging

DEFAULT_MSG_FORMAT = "%(time)s - %(message)s"

class TxtFormatter(logging.Formatter):
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt or DEFAULT_MSG_FORMAT
        logging.Formatter.__init__(self, *args, **kwargs)
        self.fmt = fmt

    def format(self, record):
        formatter = logging.Formatter(self.fmt)
        return formatter.format(record)

class ColoredFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self.fmt = fmt or DEFAULT_MSG_FORMAT
        self.FORMATS = {
            logging.DEBUG: self.grey,
            logging.INFO: self.blue,
            logging.WARNING: self.yellow,
            logging.ERROR: self.red,
            logging.CRITICAL: self.bold_red,
        }

    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record and colorize output"""
        log_msg_format = self.FORMATS.get(record.levelno, self.grey) + DEFAULT_MSG_FORMAT

        # serviceContext = getattr(record, 'serviceContext', '')
        # if record.serviceContext:
        #    format += '%(serviceContext)'
        component = getattr(record, 'component', '')
        if component:
            log_msg_format += ' %(component)s'
        else:
            log_msg_format += ' %(name)s'
        error_msg = getattr(record, 'error', '')
        if error_msg:
            log_msg_format += ' %(error)s'
        info_msg = getattr(record, 'info', '')
        if info_msg:
            log_msg_format += ' %(info)s'
        if record.exc_info:
            log_msg_format += ' %(exc_info)s'
        if record.exc_text:
            log_msg_format += ' %(exc_text)s'
        if record.stack_info:
            log_msg_format += ' %(stack_info)s'

        formatter = logging.Formatter(log_msg_format + self.reset)
        return formatter.format(record)
