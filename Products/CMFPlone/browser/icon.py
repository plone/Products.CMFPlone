# -*- coding: utf-8 -*-
from OFS.Image import File
from plone.registry.interfaces import IRegistry
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
class IconView:

    prefix = 'plone.staticresources.icon.'

    def publishTraverse(self, request, name):
        request['TraversalRequestNameStack'] = []
        return self

    def __init__(self, context, request):
        super(IconView, self).__init__(context, request)
        if len(self.request.path) == 1:
            self.icon = request.path[0]

    def __call__(self, icon=None):
        if icon:
            self.icon = icon
        name = self.icon
        url = getSite().absolute_url() + '/' + self.get_icon(name)
        return url

    def get_icon(self, name):
        registry = getUtility(IRegistry)
        icon = self.prefix + name
        if icon in registry:
            return registry[icon]
        raise LocationError(name)

    def tag(self, name, tag_class='', tag_alt=''):
        icon = self.get_icon(name)
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
                tag_src = icon,
                tag_class = tag_class,
                tag_alt = tag_alt,
            )
        return tag
