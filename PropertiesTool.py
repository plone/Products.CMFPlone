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
    meta_types = all_meta_types =  ( ( { 'name' : 'PropertySheet'
                                       , 'action' : 'manage_addPropertySheetForm' }, ) )

    manage_options = ( (Folder.manage_options[0], ) +
                        BaseTool.manage_options  )

    manage_addPropertySheetForm = PageTemplateFile('www/addPropertySheet',globals())

    def manage_addPropertySheet(self, id, title='', REQUEST=None):
        """ adds a instance of a Property Sheet """
        o=SimpleItemWithProperties(id, title)
        self._setObject(id, o)
        setattr(o, 'title', title)
        if REQUEST is not None:
            return self.manage_main()

InitializeClass(PropertiesTool)


class SimpleItemWithProperties (PropertyManager, SimpleItem):
    """
    A common base class for objects with configurable
    properties in a fixed schema.
    """
    manage_options = (
        PropertyManager.manage_options
        + SimpleItem.manage_options)


    security = ClassSecurityInfo()
    security.declarePrivate(
        'manage_addProperty',
        'manage_delProperties',
        'manage_changePropertyTypes',
        )

#    def manage_propertiesForm(self, REQUEST, *args, **kw):
#        'An override that makes the schema fixed.'
#        my_kw = kw.copy()
#        my_kw['property_extensible_schema__'] = 0
#        return apply(PropertyManager.manage_propertiesForm,
#                     (self, self, REQUEST,) + args, my_kw)

    security.declarePublic('propertyLabel')
    def propertyLabel(self, id):
        """Return a label for the given property id
        """
        for p in self._properties:
            if p['id'] == id:
                return p.get('label', id)
        return id

InitializeClass( SimpleItemWithProperties )