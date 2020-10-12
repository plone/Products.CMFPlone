# -*- coding: utf-8 -*-
from OFS.Image import File
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import adapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.location.interfaces import LocationError
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class IconView(BrowserView):

    prefix = 'plone.staticresources.icon.'
    name = 'bug'

    def publishTraverse(self, request, name):
        request['TraversalRequestNameStack'] = []
        return self

    def __init__(self, context, request):
        super(IconView, self).__init__(context, request)
        if len(self.request.path) == 1:
            self.name = request.path[0]

    def __call__(self):
        icon = self.lookup(self.name)
        return icon

    def lookup(self, name):
        registry = getUtility(IRegistry)
        icon = self.prefix + name
        if icon in registry:
            return registry[icon]
        else:
            icon = self.prefix + 'bug'
            return registry[icon]

    def url(self, name):
        url = getSite().absolute_url() + '/' + self.lookup(name)
        return url

    def tag(self, name, tag_class='', tag_alt=''):
        icon = self.lookup(name)
        if icon.endswith('.svg'):
            file = getSite().restrictedTraverse(icon)
            if isinstance(file, File):
                raise NotImplementedError(
                    'Resolve icons stored in database is not yet implemented.'
                )
            with open(file.path, 'r') as f:
                tag = f.read()
        else:
            tag = '<img src="{tag_src}" class="{tag_class}" alt="{tag_alt}" />'
            tag = tag.format(
                tag_src = self.url(name),
                tag_class = tag_class,
                tag_alt = tag_alt,
            )
        return tag
