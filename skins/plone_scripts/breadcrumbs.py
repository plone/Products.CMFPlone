## Script (Python) "breadcrumbs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=used to make the breadcrumbs in the pathbar
##
currentlyViewingFolderContents=0
path_seq = ()

o=context.portal_url.getPortalObject()

if obj is None:
    obj=context
    
relative_ids = context.portal_url.getRelativeContentPath( obj)
template_id = context.REQUEST.get('PUBLISHED', None)

if template_id and not relative_ids:
    path_seq = ( ( 'home', o.absolute_url() )
               , ( template_id.title_or_id(), o.absolute_url()+'/'+template_id.getId()) )
    return path_seq

if template_id is not None and \
    hasattr(template_id, 'getId') and \
    template_id.getId()=='folder_contents':
    currentlyViewingFolderContents=1

if currentlyViewingFolderContents and \
    context.portal_membership.checkPermission('List folder contents', o):
    path_seq = ( ('home', o.absolute_url()+'/folder_contents'), )
else:
    path_seq = ( ('home', o.absolute_url()), )

for id in relative_ids:
    try:
        o=o.restrictedTraverse(id)
        if o.getId() in ('talkback', ): # I'm sorry ;(
            raise 'talkbacks would clutter our precious breadcrumbs'
        if o.isPrincipiaFolderish and \
           context.portal_membership.checkPermission('List folder contents', o) and \
           currentlyViewingFolderContents:
            path_seq+=( (o.title_or_id(), o.absolute_url()+'/folder_contents'), )
        else:
            path_seq+=( (o.title_or_id(), o.absolute_url()), )
    except:
        pass # gulp! this usually occurs when trying to traverse into talkback objects

return path_seq



