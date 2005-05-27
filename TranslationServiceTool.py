""" 
This tool requires a translation service which supports
the utranslate method and the default parameter.
By time of writing this code, that is only valid for PTS.
"""

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFCore.utils import getToolByName
from i18nl10n import utranslate, ulocalized_time

class TranslationServiceTool(PloneBaseTool, UniqueObject, SimpleItem):
    """ Utility methods to access the translation machinery """
    
    id = 'translation_service'
    meta_type = ToolNames.TranslationServiceTool
    toolicon = 'skins/plone_images/site_icon.gif'
    security = ClassSecurityInfo()
    
    __implements__ = (PloneBaseTool.__implements__,
                      SimpleItem.__implements__, )
  
    security.declarePublic('utranslate')
    def utranslate(self, *args, **kw):
        # Translate method to access the translation service 
        # from resticted code like skins.
        return utranslate(*args, **kw)
       
    security.declarePublic('encode')
    def encode(self, m, input_encoding=None, output_encoding=None, errors='strict'):
        # encode a give unicode type or string type to string type in encoding output_encoding
        
        # check if input is not type unicode
        if not isinstance(m, unicode):
            if input_encoding is None: input_encoding = 'utf-8'
            m = unicode(str(m), input_encoding, errors)
        
        if output_encoding is None:
            # get output encoding from portal
            plone_tool = getToolByName(self, 'plone_utils')
            output_encoding = plone_tool.getSiteEncoding()
        
        # return as type string
        return m.encode(output_encoding, errors)
        
    security.declarePublic('asunicodetype')
    def asunicodetype(self, m, input_encoding=None, errors='strict'):
        # create type unicode from type string
        
        if isinstance(m, unicode): return m
            
        if input_encoding is None:
            # get input encoding from portal
            plone_tool = getToolByName(self, 'plone_utils')
            input_encoding = plone_tool.getSiteEncoding()
            
        # return as type unicode
        return unicode(str(m), input_encoding, errors)
        
    security.declarePublic('ulocalized_time')
    def ulocalized_time(self, time, long_format = None, context = None, domain='plone'):
  
        # get some context if none is passed
        if context is None: context = self

        return ulocalized_time(time, long_format, context, domain)

InitializeClass(TranslationServiceTool)
