import os

from Products.CMFPlone import custom_policies
from Products.CMFDefault.Portal import CMFSite

def listPolicies(creation=1):
    """ Float default plone to the top """
    names=[]
    for name, klass in custom_policies.items():
        available=getattr(klass, 'availableAtConstruction', None)
        if creation and available:
            names.append(name)

    default=names.pop(names.index('Default Plone'))
    names.insert(0, default)
    return names

def addPolicy(label, klass):
    custom_policies[label]=klass

from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFDefault import DublinCore
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone.PloneFolder import OrderedContainer
from Products.CMFPlone.utils import classImplements
import Globals

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute
from webdav.NullResource import NullResource
from Products.CMFPlone.PloneFolder import ReplaceableWrapper
from Products.CMFPlone.utils import log_exc
from Products.CMFPlone.utils import WWW_DIR

default_frontpage="Unable to load front-page skeleton file"
try:
    f = open(os.path.join(WWW_DIR, 'default_frontpage.html'), 'r')
except IOError:
    log_exc('Unable to open frontpage skeleton')
else:
    default_frontpage = f.read()
    f.close()
    del f

member_indexhtml="""\
member_search=context.restrictedTraverse('member_search_form')
return member_search()
"""

class PloneSite(CMFSite, OrderedContainer, BrowserDefaultMixin):
    """
    Make PloneSite subclass CMFSite and add some methods.
    This will be useful for adding more things later on.
    """
    security=ClassSecurityInfo()
    meta_type = portal_type = 'Plone Site'
    __implements__ = DublinCore.DefaultDublinCoreImpl.__implements__ + \
                     OrderedContainer.__implements__ + \
                     BrowserDefaultMixin.__implements__

    manage_renameObject = OrderedContainer.manage_renameObject

    moveObject = OrderedContainer.moveObject
    moveObjectsByDelta = OrderedContainer.moveObjectsByDelta

    # Switch off ZMI ordering interface as it assumes a slightly
    # different functionality
    has_order_support = 0
    manage_main = Globals.DTMLFile('www/main', globals())

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead
        of index_html """
        return getToolByName(self, 'plone_utils').browserDefault(self)

    def index_html(self):
        """ Acquire if not present. """
        request = getattr(self, 'REQUEST', None)
        if request and request.has_key('REQUEST_METHOD'):
            if request.maybe_webdav_client:
                method = request['REQUEST_METHOD']
                if method in ('PUT',):
                    # Very likely a WebDAV client trying to create something
                    return ReplaceableWrapper(NullResource(self, 'index_html'))
                elif method in ('GET', 'HEAD', 'POST'):
                    # Do nothing, let it go and acquire.
                    pass
                else:
                    raise AttributeError, 'index_html'
        # Acquire from skin.
        _target = self.__getattr__('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

    def manage_beforeDelete(self, container, item):
        """ Should send out an Event before Site is being deleted """
        self.removal_inprogress=1
        PloneSite.inheritedAttribute('manage_beforeDelete')(self, container, item)

    def _management_page_charset(self):
        """ Returns default_charset for management screens """
        properties = getToolByName(self, 'portal_properties', None)
        # Let's be a bit careful here because we don't want to break the ZMI
        # just because people screw up their Plone sites (however thoroughly).
        if properties is not None:
            site_properties = getattr(properties, 'site_properties', None)
            if site_properties is not None:
                getProperty = getattr(site_properties, 'getProperty', None)
                if getProperty is not None:
                    return getProperty('default_charset', 'utf-8')
        return 'utf-8'

    management_page_charset = ComputedAttribute(_management_page_charset, 1)

    def view(self):
        """ Ensure that we get a plain view of the object, via a delegation to
        __call__(), which is defined in BrowserDefaultMixin
        """
        return self()

    security.declareProtected(AccessContentsInformation,
			     'folderlistingFolderContents')
    def folderlistingFolderContents(self, spec=None, contentFilter=None):
        """Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission,
        as in CMFDefault.

        This is copied from Archetypes Basefolder and is needed by the
        reference browser.
        """
        return self.listFolderContents(spec, contentFilter)

classImplements(PloneSite, PloneSite.__implements__, ISiteRoot)
Globals.InitializeClass(PloneSite)
