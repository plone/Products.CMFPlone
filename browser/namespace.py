# Simple Namespace Handlers for some specialized URL-based functions.

import re
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.traversing.interfaces import ITraversable

from Acquisition import aq_base
from webdav.NullResource import NullResource
from Products.Five import BrowserView
from Products.CMFPlone.browser.interfaces import IPropertyBag

def shasattr(obj, attr):
    return getattr(aq_base(obj), attr, obj) is not obj

ATTR_MARKER = re.compile('\+\+(\w+):')
PROP_MARKER = re.compile('\s?:\s?')
LIST_MARKER = re.compile('\s?,\s?')

class PropertyBag(dict):
    implements(IPropertyBag)

    def apply(self, obj):
        # XXX Hardcoded for now, will use view lookup later.
        if self.has_key('description'):
            if shasattr(obj, 'setDescription'):
                obj.setDescription(self['description'])
        if self.has_key('title'):
            if shasattr(obj, 'setTitle'):
                obj.setTitle(self['title'])
        if self.has_key('subject'):
            if shasattr(obj, 'setSubject'):
                obj.setSubject(
                    LIST_MARKER.split(self['subject']) +
                    list(obj.Subject()))

class props(BrowserView):
    """Traversal adapter for the props namespace
    """
    implements(ITraversable)

    def traverse(self, name, remaining=()):
        """Collect names from the URL and temporarily stores them in the
        request for later retrieval and processing by a content rule.

        >>> class FakeRequest(object):
        ...     def __init__(self):
        ...         self._held = []
        ...     def _hold(self, obj):
        ...         self._held.append(obj)

        >>> req = FakeRequest()
        >>> view = props(None, req)

        >>> req._held
        []
 
        >>> view.traverse('subject:planet,plone,plip++description:Universe')
        >>> len(req._held)
        1

        >>> for key, value in sorted(req._held[0].items()):
        ...     print key, '||', value
        description || Universe
        subject || planet,plone,plip

        >>> req._held = []

        >>> view.traverse('title:C++ programming++description:Yadda Yadda')
        >>> len(req._held)
        1

        >>> for key, value in sorted(req._held[0].items()):
        ...     print key, '||', value
        description || Yadda Yadda
        title || C++ programming

        >>> req._held = []

        >>> view.traverse('subject:c++,language'
        ...               '++title:C++ programming'
        ...               '++description:Yadda Yadda')
        >>> len(req._held)
        1

        >>> for key, value in sorted(req._held[0].items()):
        ...     print key, '||', value
        description || Yadda Yadda
        subject || c++,language
        title || C++ programming

        >>> req._held = []

        """
        properties = ATTR_MARKER.split(name)
        properties[0:1] = PROP_MARKER.split(properties[0])
        bag = PropertyBag()
        while properties:
            bag[properties.pop()] = properties.pop()
        self.request._hold(bag)
        return self.context # XXX Check this, need to return something
                            # that can be traversed.
 
def applyProperties(ev):
    req = getattr(ev.newParent, 'REQUEST', None)
    for item in getattr(req, '_held', ()):
        if IPropertyBag.providedBy(item):
            item.apply(ev.object)
