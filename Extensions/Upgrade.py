from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod import ExternalMethod

def upgrade(self):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    if not portal.hasProperty('allowAnonymousViewAbout'):
        portal._setProperty('allowAnonymousViewAbout', 0, 'boolean')
        #outStream.write( "By default anonymous is not allowed to see the About box \n" )
    if not 'getWorklists' in self.objectIds():
        em = ExternalMethod.ExternalMethod(id='getWorklists',
                                           title='Plone worklists',
                                           module='CMFPlone.PloneWorklists',
                                           function='getWorklists')
        self._setObject('getWorklists', em)

    return 'fin'

def migrate2ColumnLayout(self):
    skin_tool=getToolByName(self, 'portal_skins')

    debug = getattr(self, 'plone_debug')

    skin_map=skin_tool._getSelections()

    map = { 'plone_ui_slots': 'plone_templates/ui_slots'
          , 'plone_mozilla': 'plone_styles/mozilla'
          , 'plone_form_scripts': 'plone_scripts/form_scripts'
          , 'plone_ie55': '' #erase plone_ie55 skin entry
          , 'plone_xp': 'plone_styles/winxp'
          }

    for skin_name, skin_path in skin_tool.getSkinPaths():
        fsdir_views = [map.get(path.strip(), path.strip()) for path in skin_path.split(',')]
        path = [p for p in fsdir_views if p]
        skin_map[skin_name]=','.join(path)


