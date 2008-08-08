import logging
import sys

MINIMUM_PYTHON_VER = (2, 4, 3)
PREFERRED_PYTHON_VER = "2.4.4 or newer"

MINIMUM_ZOPE_VER = (2, 10, 4)
PREFERRED_ZOPE_VER = "2.10.4 or newer"

MINIMUM_CMF_VER = (2, 1, 0)

messages = []

def log(message, summary='', severity=logging.ERROR, optional=0):
    if optional:
        subsys = 'Plone Option'
    else:
        subsys = 'Plone Dependency'
    messages.append({'message' : message, 'summary' : summary,
                     'severity' : severity, 'optional' : optional
            })
    logger = logging.getLogger(subsys)
    logger.log(severity, '%s \n%s', summary, message)

# test python version
PYTHON_VER = sys.version_info[:3]
if PYTHON_VER < MINIMUM_PYTHON_VER:
    log(("Python version %s found but Plone needs at least "
         "Python %s. Please download and install Python %s "
     "from http://python.org/" % (PYTHON_VER,
     MINIMUM_PYTHON_VER, PREFERRED_PYTHON_VER) ))

# test zope version
ZOPE_VER = "unknown"
try:
    from App.version_txt import getZopeVersion
except ImportError:
    pass
else:
    try:
        ZOPE_VER = getZopeVersion()[:3]
    except (ValueError, TypeError, KeyError):
        pass

if ZOPE_VER in ('unknown', (-1, -1, -1)): # -1, -1, 1 is developer release
    log(("Unable to detect Zope version. Please make sure you have Zope "
         "%s installed." % PREFERRED_ZOPE_VER), severity=logging.INFO)
elif ZOPE_VER < MINIMUM_ZOPE_VER:
    log(("Zope version %s found but Plone needs at least "
         "Zope %s Please download and install Zope %s "
     "from http://zope.org/" %
     ('.'.join([str(x) for x in ZOPE_VER]),
       '.'.join([str(x) for x in MINIMUM_ZOPE_VER]), PREFERRED_ZOPE_VER) ))
