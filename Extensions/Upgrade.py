from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.SkinsTool import _upgrade
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

    