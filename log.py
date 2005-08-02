"""
This module resolves an import order dependency.
Don't import from here, import from utils.
"""

import zLOG

# generic log method
def log(message, summary='', severity=zLOG.INFO):
    zLOG.LOG('Plone', severity, summary, message)

# log message + exception info
def log_exc(message='', summary='', severity=zLOG.ERROR):
    zLOG.LOG('Plone', severity, summary, message, error=True)

# deprecration warning
def log_deprecated(message, summary='Deprecation Warning',
                   severity=zLOG.WARNING):
    zLOG.LOG('Plone', severity, summary, message)

