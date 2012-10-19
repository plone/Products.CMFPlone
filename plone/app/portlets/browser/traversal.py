from zope.interface import implements
from zope.component import adapts, getUtility, getMultiAdapter

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.http import IHTTPRequest

from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.CMFCore.interfaces import ISiteRoot

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.storage import UserPortletAssignmentMapping
from plone.app.portlets.storage import GroupDashboardPortletAssignmentMapping

class ContextPortletNamespace(object):
    """Used to traverse to a contextual portlet assignable
    """
    implements(ITraversable)
    adapts(ILocalPortletAssignable, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        column = getUtility(IPortletManager, name=name)
        manager = getMultiAdapter((self.context, column,), IPortletAssignmentMapping)
        return manager

class DashboardNamespace(object):
    """Used to traverse to a portlet assignable for the current user for
    the dashboard.
    """
    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        col, user = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[USER_CATEGORY]
        manager = category.get(user, None)
        if manager is None:
            manager = category[user] = UserPortletAssignmentMapping(manager=col,
                                                                    category=USER_CATEGORY,
                                                                    name=user)

        # XXX: For graceful migration
        if not getattr(manager, '__manager__', None):
            manager.__manager__ = col
        if not getattr(manager, '__category__', None):
            manager.__category__ = USER_CATEGORY
        if not getattr(manager, '__name__', None):
            manager.__name__ = user

        return manager

class GroupDashboardNamespace(object):
    """Used to traverse to a portlet assignable for a group for the dashboard
    """

    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        col, group = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[GROUP_CATEGORY]
        manager = category.get(group, None)
        if manager is None:
            manager = category[group] = \
                GroupDashboardPortletAssignmentMapping(manager=col,
                                                       category=GROUP_CATEGORY,
                                                       name=group)
        return manager

class GroupPortletNamespace(object):
    """Used to traverse to a group portlet assignable
    """
    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        col, group = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[GROUP_CATEGORY]
        manager = category.get(group, None)
        if manager is None:
            manager = category[group] = PortletAssignmentMapping(manager=col,
                                                                 category=GROUP_CATEGORY,
                                                                 name=group)

        # XXX: For graceful migration
        if not getattr(manager, '__manager__', None):
            manager.__manager__ = col
        if not getattr(manager, '__category__', None):
            manager.__category__ = GROUP_CATEGORY
        if not getattr(manager, '__name__', None):
            manager.__name__ = group

        return manager

class ContentTypePortletNamespace(object):
    """Used to traverse to a content type portlet assignable
    """
    implements(ITraversable)
    adapts(ISiteRoot, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        col, pt = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[CONTENT_TYPE_CATEGORY]
        manager = category.get(pt, None)
        if manager is None:
            manager = category[pt] = PortletAssignmentMapping(manager=col,
                                                              category=CONTENT_TYPE_CATEGORY,
                                                              name=pt)

        # XXX: For graceful migration
        if not getattr(manager, '__manager__', None):
            manager.__manager__ = col
        if not getattr(manager, '__category__', None):
            manager.__category__ = CONTENT_TYPE_CATEGORY
        if not getattr(manager, '__name__', None):
            manager.__name__ = pt

        return manager
