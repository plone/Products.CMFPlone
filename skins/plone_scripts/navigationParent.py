## Script (Python) "navigationParent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None,templateId=None
##title=returns the appropriate url for the parent object
##

if obj is None: 
    obj=context

if obj.getId()=='index_html': #XXX hardcoded method name
    obj=obj.aq_parent         # we really want to know if this is a view or not.

parent=obj.aq_parent
relative_ids = context.portal_url.getRelativeContentPath(obj)

if not relative_ids:
    return
    
if not relative_ids and context.portal_membership.checkPermission('List folder contents', context):
    return context.absolute_url() + '/folder_contents'

if relative_ids:
    if parent.getId()=='talkback': #yikes, what a cheap hack
        parent=parent.aq_parent
    
    if parent.isPrincipiaFolderish and \
       context.portal_membership.checkPermission('List folder contents', parent) and \
       templateId and templateId=='folder_contents':
        return parent.absolute_url() + '/folder_contents'
    else:
        return parent.absolute_url()

