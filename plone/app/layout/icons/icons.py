from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from plone.app.layout.icons.interfaces import IContentIcon


class BaseIcon(object):
    """Helper base class for html rendering
    """

    __allow_access_to_unprotected_subobjects__ = True

    @memoize
    def html_tag(self):
        
        if not self.url:
            return None
        
        tag = '<img width="%s" height="%s" src="%s"' % (self.width, self.height, self.url,)
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

    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        path = self.brain.getIcon
        return "%s/%s" % (portal_url, path)

    @property
    def description(self):
        context = aq_inner(self.context)
        tt = getToolByName(context, 'portal_types')
        return tt.get(self.brain['portal_type']).Title()

    @property
    def title(self):
        return None


class CMFContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16

    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        path = self.obj.getIcon(1)
        return "%s/%s" % (portal_url, path)

    @property
    def description(self):
        context = aq_inner(self.context)
        tt = getToolByName(context, 'portal_types')
        return tt.get(self.obj.portal_type).Title()

    @property
    def title(self):
        return None


class FTIContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16

    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        path = self.obj.getIcon()
        return "%s/%s" % (portal_url, path)

    @property
    def description(self):
        return self.obj.Title()

    @property
    def title(self):
        return None


class PloneSiteContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16

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

    @property
    def title(self):
        return None


class DefaultContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj

    width = 16
    height = 16

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

    @property
    def title(self):
        return None
