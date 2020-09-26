"""
This module resolves an import order dependency.
Don't import from here, import from utils.
"""

import logging

logger = logging.getLogger('Plone')


# generic log method
def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s \n%s', summary, message)


# log message + exception info
def log_exc(message='', summary='', severity=logging.ERROR):
    logger.log(severity, '%s \n%s', summary, message, exc_info=True)


# deprecration warning
def log_deprecated(message, summary='Deprecation Warning',
                   severity=logging.WARNING):
    logger.log(severity, '%s \n%s', summary, message)
