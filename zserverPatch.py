from ZServer import zhttp_server
from ZServer import ZOPE_VERSION, ZSERVER_VERSION

try:
    PLONE_VERSION = open('version.txt', 'r').read().strip()
except IOError:
    PLONE_VERSION = 'Unknown'

zhttp_server.SERVER_IDENT = 'Zope/%s ZServer/%s Plone/%s' % (
    ZOPE_VERSION,
    ZSERVER_VERSION,
    PLONE_VERSION
    )
