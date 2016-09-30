# -*- coding: utf-8 -*-
from zope.interface import implementer
from Products.PageTemplates.interfaces import IUnicodeEncodingConflictResolver

from Products.CMFPlone.patches.unicodehacks import _unicode_replace


@implementer(IUnicodeEncodingConflictResolver)
class UTF8EncodingConflictResolver(object):
    """This resolver tries to decode a string from utf-8 and replaces it
       otherwise but logs a warning.
    """

    def resolve(self, context, text, expression):
        return _unicode_replace(text)

UTF8EncodingConflictResolver = UTF8EncodingConflictResolver()
