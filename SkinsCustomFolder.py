from urllib import quote
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore import CMFCorePermissions 
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

def manage_addSkinsCustomFolder (self, id, title = '', REQUEST = None):
    """ Add a new skin custom folder """
    
    ob = SkinsCustomFolder(id, title, REQUEST)
    self._setObject(id, ob)
    
    if REQUEST:
        try: u = self.DestinationURL()
        except: u = REQUEST['URL1']
        REQUEST.RESPONSE.redirect(u + '/manage_main')

manage_addSkinsCustomFolderForm = PageTemplateFile('www/addSkinsCustomFolder', globals())

class SkinsCustomFolder(Folder):
    """ skin custom folder """
   
    meta_type='Skin Custom Folder'
    
    security = ClassSecurityInfo()
    
    def __init__(self, id, title='',REQUEST=None):
        self.id = id
        self.title = title

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        self.refreshSkinTool()
        Folder.manage_afterAdd(self, item, container)

    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self, item):
        self.refreshSkinTool()
        Folder.manage_afterClone(self, item)

    security.declarePrivate('refreshSkinTool')        
    def refreshSkinTool(self):
        stool = getToolByName(self, 'portal_skins')
        stool.clearSkinCache()

    def __bobo_traverse__(self, REQUEST, name=None):
        # hook into traversal and refresh an object
        # after an edit (PSOT) or upload (PUT)
        method = self.REQUEST.get('REQUEST_METHOD', None)
        if method in ('POST', 'PUT'):
            self.refreshSkinTool()
        return getattr(self, name)
        
InitializeClass(SkinsCustomFolder)

def register(context, globals):
    context.registerClass(meta_type=SkinsCustomFolder.meta_type,
                          permission=CMFCorePermissions.ManagePortal,
                          constructors=(manage_addSkinsCustomFolderForm,
                                        manage_addSkinsCustomFolder,) )