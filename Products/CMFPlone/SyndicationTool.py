from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem


class SyndicationTool(SimpleItem):

    meta_type = 'Plone Syndication Tool'
    security = ClassSecurityInfo()

InitializeClass(SyndicationTool)
