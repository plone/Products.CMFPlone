#
# PloneTestCase
#

__version__ = '0.2.0'

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('CMFActionIcons')
ZopeTestCase.installProduct('CMFQuickInstallerTool')
ZopeTestCase.installProduct('GroupUserFolder')
ZopeTestCase.installProduct('CMFPlone')

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time


def setupPloneSite(app, id='portal', quiet=0):
    '''Creates a Plone site.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet: ZopeTestCase._print('Adding Plone Site ... ')
        user = User('PloneTestCase', '', ['Manager'], []).__of__(app.acl_users)
        newSecurityManager(None, user)
        app.manage_addProduct['CMFPlone'].manage_addSite(id, '', create_userfolder=1)
        noSecurityManager()
        get_transaction().commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


class PloneTestCase(ZopeTestCase.PortalTestCase):
    pass

