## Script (Python) "breadcrumbs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=used to make the breadcrumbs in the pathbar
##

homeDirectoryName = 'home'

if obj is None:
    obj=context
    
relative_ids = context.portal_url.getRelativeContentPath(obj)
published = context.REQUEST.get('PUBLISHED', None)
published_id = None
if published and hasattr(published, 'getId'):
    published_id = published.getId()

currentlyViewingFolderContents = (published_id == 'folder_contents')

o=context.portal_url.getPortalObject()

# add the initial breadcrumb: the home directory
if currentlyViewingFolderContents and \
    context.portal_membership.checkPermission('List folder contents', o):
    path_seq = ( (homeDirectoryName, o.absolute_url()+'/folder_contents'), )
else:
    path_seq = ( (homeDirectoryName, o.absolute_url()), )

view = None

# add breadcrumbs for directories between the root and the published object
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
            if o.getId() != 'index_html':
                # see if the object on the stack has a view action
                # XXX this seems expensive
                try:
                    view = o.getTypeInfo().getActionById('view')
                    path_seq+=( (o.title_or_id(), o.absolute_url()+'/' + view), )
                except:
                    view = None
                    path_seq+=( (o.title_or_id(), o.absolute_url()), )
    except:
        pass # gulp! this usually occurs when trying to traverse into talkback objects

# if the published object was not added to breadcrumbs above and
#    it is not a view template, add a breadcrumb for it
if published != o and not currentlyViewingFolderContents and published_id != view and published_id != 'index_html':
    try:
        url = published.absolute_url()
        try:
            url = url + published.getTypeInfo().getActionById('view')
        except:
            pass
        path_seq+=( (published.title_or_id(), url), )
    except:
        pass

