from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.container.interfaces import INameChooser
from zope.container.contained import NameChooser
from zope.container.traversal import ItemTraverser

from Acquisition import aq_base
from OFS.SimpleItem import SimpleItem

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets import constants
from plone.portlets.storage import PortletAssignmentMapping as BaseMapping

from plone.app.portlets.interfaces import IUserPortletAssignmentMapping
from plone.app.portlets.interfaces import IGroupDashboardPortletAssignmentMapping

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

class GroupDashboardPortletAssignmentMapping(PortletAssignmentMapping):
    """An assignment mapping for group dashboard portlets
    """

    implements(IGroupDashboardPortletAssignmentMapping)

    @property
    def id(self):
        manager = self.__manager__
        key = self.__name__

        return "++groupdashboard++%s+%s" % (manager, key,)

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
        """Choose a name based on a the portlet title

        >>> from plone.app.portlets.storage import PortletAssignmentMapping
        >>> mapping = PortletAssignmentMapping()

        >>> from zope.container.interfaces import INameChooser
        >>> chooser = INameChooser(mapping)

        >>> from plone.app.portlets.portlets import base
        >>> class DummyAssignment(base.Assignment):
        ...     title = u""

        >>> dummy = DummyAssignment()
        >>> dummy.title = u"A test title"

        >>> chooser.chooseName(None, dummy)
        'a-test-title'

        >>> chooser.chooseName(None, dummy)
        'a-test-title'

        >>> mapping[u'a-test-title'] = dummy
        >>> chooser.chooseName(None, dummy)
        'a-test-title-1'

        >>> dummy.title = 'RSS: http://plone.org'
        >>> chooser.chooseName(None, dummy)
        'rss-http-plone-org'

        >>> dummy.title = None
        >>> chooser.chooseName(None, dummy)
        'dummyassignment'

        >>> mapping[u'dummyassignment'] = dummy
        >>> delattr(dummy, 'title')
        >>> chooser.chooseName(None, dummy)
        'dummyassignment-1'
        """
        container = self.context

        if not name:
            name = getattr(object, 'title', None)

        if not name:
            name = object.__class__.__name__

        name = getUtility(IIDNormalizer).normalize(name)

        i = 0
        new_name = name
        while new_name in container and i <= ATTEMPTS:
            i += 1
            new_name = "%s-%d" % (name, i)

        self.checkName(new_name, object)
        return new_name