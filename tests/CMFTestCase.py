#
# CMFTestCase
#

__version__ = '0.2.0'

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('MailHost', quiet=1)

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time


def setupCMFSite(app, id='portal', quiet=0):
    '''Creates a CMF site.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet: ZopeTestCase._print('Adding CMF Site ... ')
        app.manage_addProduct['CMFDefault'].manage_addCMFSite(id, '', create_userfolder=1)
        get_transaction().commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


class CMFTestCase(ZopeTestCase.PortalTestCase):
    pass

