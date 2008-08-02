try:
    import ZServer
    zserver = 1
except:
    # deal gracefully with the case of no ZServer (i.e. python is accessing
    # the ZODB directly)
    zserver = 0

if zserver:
    from ZServer import zhttp_server
    from App.Common import package_home
    from Products.CMFPlone import cmfplone_globals
    from ZServer import ZOPE_VERSION, ZSERVER_VERSION

    from os.path import join

    try:
        file = join(package_home(cmfplone_globals), 'version.txt')
        PLONE_VERSION = open(file, 'r').read().strip()
    except IOError:
        PLONE_VERSION = 'Unknown'

    zhttp_server.SERVER_IDENT = 'Zope/%s ZServer/%s Plone/%s' % (
        ZOPE_VERSION,
        ZSERVER_VERSION,
        PLONE_VERSION
        )
