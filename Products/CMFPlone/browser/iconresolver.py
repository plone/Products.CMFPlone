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
class IconBaseResolver:

    def __init__(self, context, name):
        self.context = context
        self.name = name

    def __call__(self):
        registry = getUtility(IRegistry)
        prefix = 'plone.staticresources.icon.'
        icon = prefix + self.name
        if icon in registry:
            return registry[icon]


class IconURLResolver(IconBaseResolver):

    def __call__(self):
        value = super().__call__()
        url = getSite().absolute_url() + '/' + value
        return url


class IconTagResolver(IconBaseResolver):

    def __call__(self):
        value = super().__call__()
        if value.endswith('.svg'):
            file = getSite().restrictedTraverse(value)
            if isinstance(file, File):
                raise NotImplementedError(
                    'Resolve icons stored in database is not yet implemented.'
                )
            with open(file.path, 'r') as f:
                tag = f.read()
        else:
            tag = '<img src="{src_tag}" class="{class_tag}" alt="{alt_tag}"/>'
            tag.format(
                src_tag = value,
                class_tag = '',
                alt_tag = self.name,
            )            
        return tag


@implementer(ITraversable)
@adapter(ISiteRoot, Interface)
class IconBaseTraverser:

    resolver = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        if name:
            return self.resolver(self.context, name)
        raise LocationError(self.context, name)


class IconURLTraverser(IconBaseTraverser):

    resolver = IconURLResolver


class IconTagTraverser(IconBaseTraverser):

    resolver = IconTagResolver
