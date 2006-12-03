from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.browser.interfaces import IContentIcon


class CatalogBrainContentIcon:
    implements(IContentIcon)

    def __init__(self, context, request, brain):
        self.context = context
        self.request = request
        self.brain = brain
        self.portal_url = getToolByName(context, 'portal_url')()

    def width(self):
        return 16

    def height(self):
        return 16

    def url(self):
        path = self.brain['getIcon']
        if path is None or path == '':
            return
        path = path.split('/')[-1]
        return "%s/%s" % (self.portal_url, path)

    def description(self):
        return self.brain['portal_type']

    def title(self):
        return None


class ATCTContentIcon:
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj
        self.portal_url = getToolByName(context, 'portal_url')()

    def width(self):
        return 16

    def height(self):
        return 16

    def url(self):
        path = self.obj.getIcon(1)
        return "%s/%s" % (self.portal_url, path)

    def description(self):
        return self.obj.portal_type

    def title(self):
        return None


class FTIContentIcon:
    implements(IContentIcon)

    def __init__(self, context, request, obj):
        self.context = context
        self.request = request
        self.obj = obj
        self.portal_url = getToolByName(context, 'portal_url')()

    def width(self):
        return 16

    def height(self):
        return 16

    def url(self):
        path = self.obj.getIcon()
        return "%s/%s" % (self.portal_url, path)

    def description(self):
        return self.obj.Metatype()

    def title(self):
        return None
