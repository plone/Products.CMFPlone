import sys
import traceback
import os

import Globals
from Globals import HTMLFile, InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from OFS.ObjectManager import checkValidId
from OFS.PropertyManager import PropertyManager

from AccessControl import ClassSecurityInfo
#from Acquisition import aq_base, aq_inner, aq_parent
from App.Common import package_home

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore import CMFCorePermissions

from interfaces.PloneControlPanel import IControlPanel

NoGroupException = "The group doesn't exist"

class PloneConfiglet(SimpleItem, PropertyManager):
    ''' class storing information about an product'''

    meta_type="PloneConfiglet"
    security = ClassSecurityInfo()
    permission=None
    
    _properties=(
        {'id':'appId','type':'string'},
        {'id':'label','type':'string'},
        {'id':'group','type':'selection','select_variable':'getGroupIds'},
        {'id':'templateUrl','type':'string'},
        {'id':'imageUrl','type':'string'},
        {'id':'permission','type':'string'},
    )

    manage_options=PropertyManager.manage_options
    
    def __init__(self, id, appId, label, templateUrl, group, imageUrl, permission):
        self.id = id
        self.appId = appId
        self.label = label
        self.group = group
        self.templateUrl = templateUrl
        self.imageUrl = imageUrl
        self.permission = permission

    def getId(self):
        return self.id

    def getAppId(self):
        return self.appId

    def getLabel(self):
        return self.label

    def getGroup(self):
        return self.group

    def getTemplateURL(self):
        return self.templateUrl

    def getImageURL(self):
        return self.imageUrl
    
    def getPermission(self):
        return self.permission

def addControlPanelTool(self, REQUEST=None):
    """ add tool to Plone instance """
    panel = PloneControlPanel()
    self._setObject('portal_configuration', panel, set_owner=0)
    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

default_configlets = (
    {'id':'QuickInstaller','appId':'QuickInstaller','label':'Install Products',
        'templateUrl':'prefs_install_products_form','group':'Plone','permission': ManagePortal},
    {'id':'PloneReconfig','appId':'Plone','label':'Reconfigure Portal',
        'templateUrl':'reconfig_form','group':'Plone','permission': ManagePortal},
)
class PloneControlPanel( UniqueObject,  ObjectManager, SimpleItem, PropertyManager  ):
    __implements__ = (IControlPanel,)
    groups = ['Plone|Plone System', 'Products|Registered Products']
    
    meta_type = 'Plone Control Panel'
    meta_types = all_meta_types = ((
        { 'name'   : 'PloneConfiglet',
          'action' : 'addConfigletForm'},
        ))

    _properties=(
        {'id':'groups','type':'lines'},
        )
        
    id = 'portal_configuration'
    manage_options =  ObjectManager.manage_options + PropertyManager.manage_options
    #index_html=controlPanel=PageTemplateFile('www/ploneControlPanel.pt',globals())
    addConfigletForm=PageTemplateFile('www/addConfigletForm.pt',globals())

    security = ClassSecurityInfo()

    def __init__(self):
        self.id = 'portal_configuration'
        
        #register the standard configlets
        for conf in default_configlets:
            self.registerConfiglet(**conf)

    security.declareProtected('registerConfiglet',ManagePortal)
    def registerConfiglet(self, id, appId='', label='',  templateUrl='', group='Products', url='', imageUrl='', permission='', REQUEST=None):
        """ Registration of a Configlet """
        try:
            # check id
            checkValidId(self, id)
            # check existance of group
            if group not in self.getGroupIds():
                raise NoGroupException
            self, id, appId, label, templateUrl, group, imageUrl, permission
            ic = PloneConfiglet(id, appId, label, templateUrl, group, imageUrl, permission)
            self._setObject(id, ic)
        except:
            traceback.print_exc()
            raise

        if REQUEST:
            return REQUEST.RESPONSE.redirect('manage_main')

    security.declareProtected('unregisterConfiglet',ManagePortal)
    def unregisterConfiglet(self, configletId):
        """ unregister Configlet """
        try:
            self._delObject(configletId)
        except:
            traceback.print_exc()
            raise

    security.declareProtected('unregisterApplication',ManagePortal)
    def unregisterConfiglets(self, appId):
        """ unregister Configlet """
        raise 'NotYetImplemented'

    security.declarePublic('getGroupIds')
    def getGroupIds(self):
        """ list of the groups """
        return [g.split('|')[0] for g in self.groups]

    security.declarePublic('getGroups')
    def getGroups(self):
        """ list of groups as dicts """
        return [{'id':g.split('|')[0],'title':g.split('|')[-1]} for g in self.groups]
        
    security.declarePublic('enumConfiglet')
    def enumConfiglets(self, group, appId=None):
        """ lists of Configlets of a group """
        return [cobj for cobj in self.objectValues() if cobj.getGroup() == group]

    def index_html(self,REQUEST):
        return REQUEST.REDIRECT('plone_control_panel')
    
InitializeClass( PloneControlPanel )
