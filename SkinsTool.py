from Products.CMFCore.SkinsTool import modifiedOptions
from Products.CMFCore import SkinsTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
import os
from Globals import DTMLFile, PersistentMapping, package_home, InitializeClass
from Persistence import Persistent

_forms = os.path.join( package_home( globals() ), 'tool_forms' )
DefaultSkinsTool=SkinsTool.SkinsTool

class SkinsTool(DefaultSkinsTool):
    """ Plone customized SkinsTool Tool """
    
    plone_tool = 1
    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overviewForm' }
                     , { 'label' : 'Presets', 'action' : 'manage_presetsForm' } 
                     ) + modifiedOptions()
   
    manage_overviewForm = DTMLFile( 'explainSkinsTool', _forms )    
    manage_presetsForm = PageTemplateFile ('color_preset_form', _forms)

    def __init__(self):
        """ construct our skins tool """
        DefaultSkinsTool.__init__(self)
        self.color_presets = PersistentMapping()
        self.default_preset = ''
        
    security.declareProtected(CMFCorePermissions.ManagePortal, 'listPresets')
    def listPresets(self):
        """ returns a listing of tuples (id, preset_map) """ 
        _presets = []
        color_presets = self.color_presets.keys()
        color_presets.sort()
        if color_presets:
            for k in color_presets:
                _presets.append( self.color_presets[k] )           
        return _presets
        
    security.declareProtected(CMFCorePermissions.ManagePortal, 'setDefaultColorPreset')
    def setDefaultColorPreset(self, preset_id):
        self.default_preset=preset_id

    def manage_preset(self, REQUEST=None):
        """ responsible for setting a Preset """
        
    def manage_presets(self, default_preset=None, REQUEST=None):
        """ deletes, sets default, edits, adds a preset """
        return None
        
    def _addPreset(self, preset):
        """adds a preset """        
        id = preset.get('id', None)
        if id is not None:        
            self.color_presets[id]=preset
        
class ColorPreset(PersistentMapping):
    """ represents a color preset bundle, only if we were 2.2 ;) """   
    security=ClassSecurityInfo()
    security.declareObjectPublic()
                
InitializeClass(ColorPreset)
            
            
def _populate(self):
    """ pre-populates the skin tool with test data """
    turducken = {} #yum ;p
    turducken['id'] = 'turducken'
    turducken['title'] = 'Part Turkey, Part Duck, Part Chicken'   
    turducken['presets'] = []
    
    _presets = []
    a = ColorPreset()
    a['id']='mainBackground'
    a['value']='#31313'
    a['description']='color the main template background'
    
    b = ColorPreset()
    b['id']='mainTextColor'
    b['value']='#1a1a1a'
    b['description']='color of all text labels'
    
    _presets.append(a)
    _presets.append(b)  
    turducken['presets']=_presets
    skin_tool=getToolByName(self, 'portal_skins')
    skin_tool._addPreset(turducken)
                 
def _upgrade(self, skinToolObject):
    """ given a old instance of a skinToolObject, we will repopulate ourself """
    attrs = {}
    attrs['selections'] = skinToolObject.selections
    attrs['default_skin'] = skinToolObject.default_skin
    attrs['allow_any'] = skinToolObject.allow_any
    attrs['cookie_persistence'] = skinToolObject.cookie_persistence
    attrs['request_varname'] = skinToolObject.request_varname
    p = self.portal_url.getPortalObject()
    p.manage_delObjects('portal_skins')
    p.manage_addProduct['CMFPlone'].manage_addTool(type='CMF Skins Tool')
    o=getattr(p, 'portal_skins')
    for key in attrs.keys():
        setattr(o, key, attrs[key])
    return 'success'        
