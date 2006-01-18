#
# PloneTestCase
#

# $Id$

from Testing import ZopeTestCase

# XXX: Suppress DeprecationWarnings
import warnings
warnings.simplefilter('ignore', DeprecationWarning, append=1)

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFUid', quiet=1)
ZopeTestCase.installProduct('CMFActionIcons')
ZopeTestCase.installProduct('CMFQuickInstallerTool')
ZopeTestCase.installProduct('CMFFormController')
ZopeTestCase.installProduct('ResourceRegistries')
ZopeTestCase.installProduct('GroupUserFolder')
ZopeTestCase.installProduct('ZCTextIndex')
ZopeTestCase.installProduct('ExtendedPathIndex')
ZopeTestCase.installProduct('SecureMailHost')
if ZopeTestCase.hasProduct('ExternalEditor'):
    ZopeTestCase.installProduct('ExternalEditor')
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('PageTemplates', quiet=1)
ZopeTestCase.installProduct('PythonScripts', quiet=1)
ZopeTestCase.installProduct('ExternalMethod', quiet=1)

# PAS
ZopeTestCase.installProduct('PluggableAuthService')
ZopeTestCase.installProduct('PluginRegistry')
ZopeTestCase.installProduct('PasswordResetTool')
ZopeTestCase.installProduct('PlonePAS')

# Archetypes/ATContentTypes dependencies
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('ATContentTypes')
ZopeTestCase.installProduct('ATReferenceBrowserWidget')

import transaction
from Testing.ZopeTestCase.utils import makelist
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.tests.utils import setupBrowserIdManager

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
import time

from zope.app.tests.placelesssetup import setUp, tearDown
from Products.Five import zcml
import Products.statusmessages

portal_name = 'portal'
portal_owner = 'portal_owner'
default_user = ZopeTestCase.user_name
default_password = ZopeTestCase.user_password


class PloneTestCase(ZopeTestCase.PortalTestCase):
    '''TestCase for Plone testing'''

    def beforeSetUp(self):
        setUp()
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.statusmessages)

    def _setup(self):
        ZopeTestCase.PortalTestCase._setup(self)
        # Hack ACTUAL_URL and plone_skin into the REQUEST
        self.app.REQUEST['ACTUAL_URL'] = self.app.REQUEST.get('URL')
        self.app.REQUEST['plone_skin'] = 'Plone Default'
        # Need PARENTS in request otherwise REQUEST.clone() fails
        self.app.REQUEST.set('PARENTS', [self.app])
        # Disable the constraintypes performance hog
        self.folder.setConstrainTypesMode(0)

    def getPortal(self):
        '''Returns the portal object to the bootstrap code.
           DO NOT CALL THIS METHOD! Use the self.portal
           attribute to access the portal object from tests.
        '''
        return self.app[portal_name]

    def createMemberarea(self, member_id):
        '''Creates a minimal, no-nonsense memberarea.'''
        _createHomeFolder(self.portal, member_id)

    def setGroups(self, groups, name=default_user):
        '''Changes the specified user's groups. Assumes GRUF.'''
        uf = self.portal.acl_users
        uf._updateUser(name, groups=makelist(groups), domains=[])
        if name == getSecurityManager().getUser().getId():
            self.login(name)

    def loginPortalOwner(self):
        '''Use if - AND ONLY IF - you need to manipulate the
           portal object itself.
        '''
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)

    def beforeTearDown(self):
        tearDown()


class FunctionalTestCase(ZopeTestCase.Functional, PloneTestCase):
    '''Convenience class for functional unit testing'''


def setupPloneSite(app=None, id=portal_name, quiet=0, with_default_memberarea=1):
    '''Creates a Plone site.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet: ZopeTestCase._print('Adding Plone Site ... ')
        # Add user and log in
        app.acl_users._doAddUser(portal_owner, '', ['Manager'], [])
        user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
        newSecurityManager(None, user)
        # Add Plone Site
        setUp() # we need the component architecture for site generation
        factory = app.manage_addProduct['CMFPlone']
        factory.manage_addSite(id, '', create_userfolder=1)
        # Precreate default memberarea for performance reasons
        if with_default_memberarea:
            _createHomeFolder(app[id], default_user, 0)
        tearDown() # clean up again
        # Log out
        noSecurityManager()
        transaction.commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


def _createHomeFolder(portal, member_id, take_ownership=1):
    '''Creates a memberarea if it does not already exist.'''
    membership = portal.portal_membership
    members = membership.getMembersFolder()

    if not hasattr(aq_base(members), member_id):
        # Create home folder
        _createObjectByType('Folder', members, id=member_id)

    if take_ownership:
        user = portal.acl_users.getUserById(member_id)
        if user is None:
            raise ValueError, 'Member %s does not exist' % member_id
        if not hasattr(user, 'aq_base'):
            user = user.__of__(portal.acl_users)
        # Take ownership of home folder
        home = membership.getHomeFolder(member_id)
        home.changeOwnership(user)
        home.__ac_local_roles__ = None
        home.manage_setLocalRoles(member_id, ['Owner'])


def optimize():
    '''Significantly reduces portal creation time.'''
    # Don't compile expressions on creation
    def __init__(self, text):
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__
    # Don't clone actions but convert to list only
    def _cloneActions(self):
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions
    # Don't setup default directory views
    def setupDefaultSkins(self, p):
        from Products.CMFCore.utils import getToolByName
        ps = getToolByName(p, 'portal_skins')
        ps.manage_addFolder(id='custom')
        ps.addSkinSelection('Basic', 'custom')
    from Products.CMFPlone.Portal import PloneGenerator
    PloneGenerator.setupDefaultSkins = setupDefaultSkins
    # Don't setup default Members folder
    def setupMembersFolder(self, p):
        pass
    PloneGenerator.setupMembersFolder = setupMembersFolder
    # Don't setup Plone content (besides Members folder)
    def setupPortalContent(self, p):
        _createObjectByType('Large Plone Folder', p, id='Members', title='Members')
    PloneGenerator.setupPortalContent = setupPortalContent
    # Don't populate type fields in the ConstrainTypesMixin schema, FFS!
    def _ct_defaultAddableTypeIds(self):
        return []
    from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixin
    ConstrainTypesMixin._ct_defaultAddableTypeIds = _ct_defaultAddableTypeIds


optimize()

# Create a Plone site in the test (demo-) storage
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog()
setupBrowserIdManager(app)
setupPloneSite(app)
ZopeTestCase.close(app)
