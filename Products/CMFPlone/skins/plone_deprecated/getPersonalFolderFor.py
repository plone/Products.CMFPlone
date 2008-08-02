## Script (Python) "getPlonePersonalFolderFor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=None
##title=
##

#NOTE
#This script is here because when you use a 3rd party
#portal_membership there are places in plone (personalize_form)
#that look for this method.  If the tool doesnt support it
#this script is acquired.

context.plone_log("The getPersonalFolderFor script is deprecated and will be "
                  "removed in Plone 4.0.")

folder=context.portal_membership.getHomeFolder(member)
return getattr(folder,'.personal', None)
