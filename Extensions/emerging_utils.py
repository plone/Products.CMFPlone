from Products.CMFCore.utils import getToolByName
def bindSkin(self, REQUEST=None):
	REQUEST=getattr(self, 'REQUEST', None)
	portal = getToolByName(self, 'portal_url').getPortalObject()
	if REQUEST:
		portal._v_skindata=( self.getSkinByName('Emerging Website'), {} )


