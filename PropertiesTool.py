from ComputedAttribute import ComputedAttribute
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFDefault.PropertiesTool import PropertiesTool as BaseTool
from Products.CMFPlone import ToolNames

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from Globals import InitializeClass

from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces.PropertiesTool import IPropertiesTool
from Products.CMFPlone.utils import classImplements

class PropertiesTool(PloneBaseTool, Folder, BaseTool):

    id = BaseTool.id
    toolicon = 'skins/plone_images/topic_icon.gif'

    meta_type = ToolNames.PropertiesTool
    meta_types = all_meta_types =  ((
        {'name' : 'Plone Property Sheet',
         'action' : 'manage_addPropertySheetForm'
         },
        ))

    __implements__ = ((IPropertiesTool,) +
                      (PloneBaseTool.__implements__,
                      ActionProviderBase.__implements__,
                      Folder.__implements__, ))

    manage_options = ((Folder.manage_options[0],) +
                        BaseTool.manage_options)

    manage_addPropertySheetForm = PageTemplateFile('www/addPropertySheet',
                                                   globals())

    security = ClassSecurityInfo()

    def title(self):
        """ Return BaseTool title
        """
        return BaseTool.title(self)

    title = ComputedAttribute(title, 1)

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
        # keep this bit of hackery for backwards compatibility
        if props.has_key('smtp_server'):
            self.MailHost.smtp_host = props['smtp_server']
        if hasattr(self, 'propertysheets'):
            ps = self.propertysheets
            if hasattr(ps, 'props'):
                ps.props.manage_changeProperties(props)


PropertiesTool.__doc__ = BaseTool.__doc__

classImplements(PropertiesTool, PropertiesTool.__implements__)
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

InitializeClass(SimpleItemWithProperties)
