from Acquisition import aq_parent, aq_inner
from Products.CMFCore.permissions import ManagePortal
from Products.CMFDefault.PropertiesTool import PropertiesTool as BaseTool

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from App.class_init import InitializeClass
from zope.interface import implements

from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces import IPropertiesTool, ISimpleItemWithProperties


class PropertiesTool(PloneBaseTool, Folder, BaseTool):

    id = BaseTool.id
    toolicon = 'skins/plone_images/topic_icon.png'

    meta_type = 'Plone Properties Tool'
    meta_types = ((
        {'name': 'Plone Property Sheet',
         'action': 'manage_addPropertySheetForm'},
        ))

    implements(IPropertiesTool)

    manage_options = ((Folder.manage_options[0], ) +
                        BaseTool.manage_options)

    manage_addPropertySheetForm = PageTemplateFile('www/addPropertySheet',
                                                   globals())

    security = ClassSecurityInfo()

    def all_meta_types(self, interfaces=None):
        return self.meta_types

    def title(self):
        """ Return BaseTool title
        """
        return BaseTool.title(self)

    security.declareProtected(ManagePortal, 'addPropertySheet')
    def addPropertySheet(self, id, title='', propertysheet=None):
        """ Add a new PropertySheet
        """
        o = SimpleItemWithProperties(id, title)

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

    security.declareProtected(ManagePortal, 'manage_addPropertySheet')
    def manage_addPropertySheet(self, id, title='',
                                propertysheet=None, REQUEST=None):
        """ Add a instance of a Property Sheet if handed a
        propertysheet put the properties into new propertysheet.
        """
        self.addPropertySheet(id, title, propertysheet)

        if REQUEST is not None:
            return self.manage_main()

    #
    #   'portal_properties' interface methods
    #
    security.declareProtected(ManagePortal, 'editProperties')
    def editProperties(self, props):
        """Change portal settings
        """
        aq_parent(aq_inner(self)).manage_changeProperties(props)
        if hasattr(self, 'propertysheets'):
            ps = self.propertysheets
            if hasattr(ps, 'props'):
                ps.props.manage_changeProperties(props)


PropertiesTool.__doc__ = BaseTool.__doc__

InitializeClass(PropertiesTool)


class SimpleItemWithProperties (PropertyManager, SimpleItem):
    """
    A common base class for objects with configurable
    properties in a fixed schema.
    """

    implements(ISimpleItemWithProperties)

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    meta_type = 'Plone Property Sheet'

    manage_options = (PropertyManager.manage_options
                     + SimpleItem.manage_options)

InitializeClass(SimpleItemWithProperties)
