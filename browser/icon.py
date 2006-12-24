from zope.interface import implements

# Caused by the remaining module alias to browser.plone (now browser.ploneview)
import sys
memoize = sys.modules['plone.memoize.instance'].memoize

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import IContentIcon

class BaseIcon(object):
    """Helper base class for html rendering
    """
    
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
        self.portal_url = getToolByName(context, 'portal_url')()

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
        self.portal_url = getToolByName(context, 'portal_url')()

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
        self.portal_url = getToolByName(context, 'portal_url')()

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
        self.portal_url = getToolByName(context, 'portal_url')()

    width = 16
    height = 16

    @property
    def url(self):
        return "%s/site_icon.gif" % self.portal_url

    @property
    def description(self):
        return self.obj.Title

    @property
    def title(self):
        return None