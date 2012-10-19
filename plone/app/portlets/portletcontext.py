from types import StringTypes

from zope.interface import implements, Interface
from zope.component import adapts

from Acquisition import aq_parent, aq_inner, aq_base

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletContext
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY


class ContentContext(object):
    """A portlet context for regular content items.

    Note - we register this for Interface so that it can also work for
    tools and other non-content items. This may hijack the context in non-CMF
    contexts, but that is doubtfully going to be an issue.
    """
    implements(IPortletContext)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    @property
    def uid(self):
        return '/'.join(self.context.getPhysicalPath())

    def getParent(self):
        return aq_parent(aq_inner(self.context))

    def globalPortletCategories(self, placeless=False):
        cats = []
        if not placeless:
            pt = self._getContentType()
            if pt is not None:
                cats.append((CONTENT_TYPE_CATEGORY, pt))
        u = self._getUserId()
        if u is not None:
            cats.append((USER_CATEGORY, u))
        for g in self._getGroupIds():
            cats.append((GROUP_CATEGORY, g))
        return cats

    def _getUserId(self):
        membership = getToolByName(self.context, 'portal_membership', None)
        if membership is None:
            return None

        member = membership.getAuthenticatedMember()
        if not member:
            return None

        memberId = member.getId()
        if memberId is None:
            # Basic users such as the special Anonymous users have no
            # id, but we can use their username instead.
            try:
                memberId = member.getUserName()
            except AttributeError:
                pass

        if not memberId:
            return None

        return memberId

    def _getGroupIds(self):
        membership = getToolByName(self.context, 'portal_membership', None)
        if membership is None or membership.isAnonymousUser():
            return ()

        member = membership.getAuthenticatedMember()
        if not member:
            return ()

        groups = hasattr(member, 'getGroups') and member.getGroups() or []

        # Ensure we get the list of ids - getGroups() suffers some acquision
        # ambiguity - the Plone member-data version returns ids.

        for group in groups:
            if type(group) not in StringTypes:
                return ()

        return sorted(groups)

    def _getContentType(self):
        typeInfo = getattr(aq_base(self.context), 'getTypeInfo', None)
        if typeInfo is not None:
            fti = typeInfo()
            if fti is not None:
                return fti.getId()
        portal_type = getattr(aq_base(self.context), 'portal_type', None)
        if portal_type is not None:
            return portal_type
        return None


class PortalRootContext(ContentContext):
    """A portlet context for the site root.
    """

    implements(IPortletContext)
    adapts(ISiteRoot)

    def __init__(self, context):
        self.context = context

    def getParent(self):
        return None
