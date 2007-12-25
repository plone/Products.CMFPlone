from zope.interface import implements
from zope.component import adapts

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.container.interfaces import INameChooser
from zope.app.container.contained import NameChooser

from zope.app.container.traversal import ItemTraverser

from Acquisition import aq_base
from OFS.SimpleItem import SimpleItem

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets import constants
from plone.portlets.storage import PortletAssignmentMapping as BaseMapping

from plone.app.portlets.interfaces import IUserPortletAssignmentMapping

ATTEMPTS = 10000

category_to_name = {
    constants.CONTEXT_CATEGORY      : 'contextportlets',
    constants.USER_CATEGORY         : 'dashboard',
    constants.GROUP_CATEGORY        : 'groupportlets',
    constants.CONTENT_TYPE_CATEGORY : 'contenttypeportlets',
}

class PortletAssignmentMapping(BaseMapping, SimpleItem):
    """A Zope 2 version of the default assignment mapping storage.
    """
    
    @property
    def id(self):
        manager = self.__manager__
        category = self.__category__
        key = self.__name__
        
        prefix = category_to_name.get(category, category)
        suffix = manager
        
        if category != constants.CONTEXT_CATEGORY and key:
            suffix = "%s+%s" % (manager, key)
        
        return "++%s++%s" % (prefix, suffix)
    
    def __setitem__(self, key, assignment):
        BaseMapping.__setitem__(self, key, aq_base(assignment))

class UserPortletAssignmentMapping(PortletAssignmentMapping):
    """An assignment mapping for user/dashboard portlets
    """

    implements(IUserPortletAssignmentMapping)
        
class PortletAssignmentMappingTraverser(ItemTraverser):
    """A traverser for portlet assignment mappings, that is acqusition-aware
    """
    implements(IBrowserPublisher)
    adapts(IPortletAssignmentMapping, IDefaultBrowserLayer)
    
    def publishTraverse(self, request, name):
        ob = ItemTraverser.publishTraverse(self, request, name)
        return ob.__of__(self.context)

class PortletsNameChooser(NameChooser):
    """A name chooser for portlets
    """
    
    implements(INameChooser)
    
    def __init__(self, context):
        self.context = context

    def chooseName(self, name, object):
        container = self.context

        if not name:
            name = object.title

        if not name:
            name = object.__class__.__name__
            
        name = name.lower()

        i = 1
        new_name = "%s-%d" % (name, i)
        while new_name in container and i <= ATTEMPTS:
            i += 1
            new_name = "%s-%d" % (name, i)
            
        self.checkName(new_name, object)
        return new_name