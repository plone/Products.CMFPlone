from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import getSecurityManager

from StringIO import StringIO
import zLOG

def log(message,summary='',severity=0):
	zLOG.LOG('MyDebugLog',severity,summary,message)

def bindSkin(self, REQUEST=None):
	""" binds a skin to the REQUEST """	
	portal = getToolByName(self, 'portal_url').getPortalObject()
	if REQUEST:
		portal._v_skindata=( self.getSkinByName('Emerging Website'), {} )


