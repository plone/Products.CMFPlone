from Products.CMFDefault.PropertiesTool import PropertiesTool as BaseTool
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from Globals import InitializeClass

#from Products.CMFCore.utils SimpleItemWithProperties
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

class PropertiesTool(Folder, BaseTool):
    """ Specialized PropertiesTool that contains PropertySheets """
    id = 'portal_properties'

    meta_type = 'Plone Properties Tool'
    meta_types = all_meta_types =  ( ( { 'name' : 'Plone Property Sheet'
                                       , 'action' : 'manage_addPropertySheetForm' }, ) )

    manage_options = ( (Folder.manage_options[0], ) +
                        BaseTool.manage_options  )

    manage_addPropertySheetForm = PageTemplateFile( 'www/addPropertySheet'
                                                  , globals() )

    def title(self):
        """ return BaseTool title """
        return BaseTool.title(self)

    def addPropertySheet(self, id, title='', propertysheet=None):
        """ add a new PropertySheet """
        o=SimpleItemWithProperties(id, title)

        # copy the propertysheet values onto the new instance
        if propertysheet is not None:
            if not hasattr(propertysheet, 'propertyIds'):
                raise TypeError, 'propertysheet needs to be a PropertyManager'

            for property in propertysheet.propertyMap():
                pid=property.get('id')
                ptype=property.get('type')
                pvalue=propertysheet.getProperty(pid)
                if not hasattr(o, pid):
                    o._setProperty(pid, pvalue, ptype)
                
        self._setObject(id, o)

            
    def manage_addPropertySheet(self, id, title='', propertysheet=None, REQUEST=None):
        """ adds a instance of a Property Sheet 
            if handed a propertysheet put the
            properties into new propertysheet.
        """
        self.addPropertySheet(id, title, propertysheet)
        
        if REQUEST is not None:
            return self.manage_main()

InitializeClass(PropertiesTool)


class SimpleItemWithProperties (PropertyManager, SimpleItem):
    """
    A common base class for objects with configurable
    properties in a fixed schema.
    """
    
    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    meta_type = 'Plone Property Sheet'

    manage_options = ( PropertyManager.manage_options
                     + SimpleItem.manage_options)

InitializeClass( SimpleItemWithProperties )
