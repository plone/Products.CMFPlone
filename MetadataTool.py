from Products.CMFDefault.MetadataTool import MetadataTool as BaseTool
from Globals import InitializeClass, DTMLFile

class MetadataTool( BaseTool ):

    id = 'portal_metadata'
    meta_type = 'Plone Metadata Tool'

InitializeClass( MetadataTool )
