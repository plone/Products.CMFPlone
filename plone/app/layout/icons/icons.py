from Acquisition import aq_inner
from zope.interface import implements

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
        self.portal_url = getToolByName(aq_inner(context), 'portal_url')()

    width = 16
    height = 16

    @property
    def url(self):
        path = self.brain['getIcon']
        if path is None or path == '':
            return
        path = path.split('/')[-1]
        return "%s/%s" % (self.portal_url, path)

    @property
    def description(self):
        return self.brain['portal_type']

    @property
    def title(self):
        return None


class ArchetypesContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj
        self.portal_url = getToolByName(aq_inner(context), 'portal_url')()

    width = 16
    height = 16

    @property
    def url(self):
        path = self.obj.getIcon(1)
        return "%s/%s" % (self.portal_url, path)

    @property
    def description(self):
        return self.obj.portal_type

    @property
    def title(self):
        return None


class FTIContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj
        self.portal_url = getToolByName(aq_inner(context), 'portal_url')()

    width = 16
    height = 16

    @property
    def url(self):
        path = self.obj.getIcon()
        return "%s/%s" % (self.portal_url, path)

    @property
    def description(self):
        return self.obj.Metatype()

    @property
    def title(self):
        return None


class PloneSiteContentIcon(BaseIcon):
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj
        self.portal_url = getToolByName(aq_inner(context), 'portal_url')()

    width = 16
    height = 16

    @property
    def url(self):
        return "%s/site_icon.gif" % self.portal_url

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
        self.portal_url = getToolByName(aq_inner(context), 'portal_url')()

    width = 16
    height = 16

    @property
    def url(self):
        if self.obj is None:
            return None
        return "%s/error_icon.gif" % self.portal_url

    @property
    def description(self):
        if self.obj is None:
            return None
        return self.obj.Title

    @property
    def title(self):
        return None
