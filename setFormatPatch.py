"""Monkey patch DublinCore to work around
   http://plone.org/collector/1323
"""
from Acquisition import aq_base

def setFormat( self, format ):
    """
        Dublin Core element - resource format
    """
    self.__old_setFormat(format)
    # Update the content_type property if present
    if (getattr(aq_base(self), 'hasProperty', None) and
        self.hasProperty('content_type')):
        self.manage_changeProperties(content_type=format)

from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
if not hasattr(DefaultDublinCoreImpl, '__old_setFormat'):
    DefaultDublinCoreImpl.__old_setFormat = DefaultDublinCoreImpl.setFormat
    DefaultDublinCoreImpl.setFormat = setFormat
