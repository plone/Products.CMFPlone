from plone.memoize.instance import memoize
from zope.component import getMultiAdapter
from zope.interface import implements

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName

from plone.app.layout.icons.interfaces import IContentIcon


class BaseIcon(object):
    """Helper base class for html rendering
    """

    __allow_access_to_unprotected_subobjects__ = True

    def __call__(self):
        return self.html_tag()

    @memoize
    def html_tag(self):

        if not self.url:
            return None

        tag = '<img width="%s" height="%s" src="%s"' % (self.width, self.height, self.url)
        if self.title:
            tag += ' title="%s"' % self.title
        if self.description:
            tag += ' alt="%s"' % self.description
        tag += ' />'
        return tag


class CatalogBrainContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, brain):
        self.context = context
        self.request = request
        self.brain = brain

    width = 16
    height = 16
    title = None

    @property
    def url(self):
        path = self.brain.getIcon
        if not path:
            return path

        portal_state_view = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        portal_url = portal_state_view.portal_url()
        return "%s/%s" % (portal_url, path)

    @property
    def description(self):
        context = aq_inner(self.context)
        tt = getToolByName(context, 'portal_types')
        fti = tt.get(self.brain['portal_type'])
        if fti is not None:
            return fti.Title()
        else:
            return self.brain['portal_type']


class CMFContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16
    title = None

    @property
    def url(self):
        path = self.obj.getIcon(1)
        if not path:
            return path

        portal_url = getToolByName(self.context, 'portal_url')()
        return "%s/%s" % (portal_url, path)

    @property
    def description(self):
        context = aq_inner(self.context)
        tt = getToolByName(context, 'portal_types')
        fti = tt.get(self.obj.portal_type)
        if fti is not None:
            return fti.Title()
        else:
            return self.obj.portal_type


class FTIContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16
    title = None

    @property
    def url(self):
        context = self.context
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()

        ec = createExprContext(aq_parent(context), portal, context)
        icon = self.obj.getIconExprObject()
        path = ''
        if icon:
            path = icon(ec)
        return path

    @property
    def description(self):
        return self.obj.Title()


class PloneSiteContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16
    title = None

    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        if portal_state.is_rtl():
            return "%s/rtl-site_icon.gif" % portal_url
        else:
            return "%s/site_icon.gif" % portal_url

    @property
    def description(self):
        return self.obj.Title()


class DefaultContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16
    title = None

    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        if self.obj is None:
            return None
        return "%s/error_icon.gif" % portal_url

    @property
    def description(self):
        if self.obj is None:
            return None
        return self.obj.Title()
