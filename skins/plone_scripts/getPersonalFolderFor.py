## Script (Python) "getPlonePersonalFolderFor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=None
##title=
##
folder=context.portal_membership.getHomeFolder(member)
return getattr(folder,'.personal', None)
