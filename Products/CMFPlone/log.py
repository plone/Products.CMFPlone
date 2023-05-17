"""
This module resolves an import order dependency.
Don't import from here, import from utils.
"""
from zope.deprecation import deprecate

import logging


logger = logging.getLogger("Plone")


# generic log method
def log(message, summary="", severity=logging.INFO):
    logger.log(severity, "%s \n%s", summary, message)


# log message + exception info
def log_exc(message="", summary="", severity=logging.ERROR):
    logger.log(severity, "%s \n%s", summary, message, exc_info=True)


# deprecration warning
@deprecate(
    "Use a recommended deprecation method, see Plone Deprecation Guide: "
    "https://docs.plone.org/develop/styleguide/deprecation.html "
    "(will be removed in Plone 7.0)"
)
def log_deprecated(message, summary="Deprecation Warning", severity=logging.WARNING):
    logger.log(severity, "%s \n%s", summary, message)
