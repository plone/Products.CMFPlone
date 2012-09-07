from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem


class SyndicationTool(SimpleItem):
    """
    No longer used. Just stub so uninstall goes smoothly
    """
    meta_type = 'Plone Syndication Tool'
    security = ClassSecurityInfo()

InitializeClass(SyndicationTool)
