## Script (Python) "wikipage_deleterename_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE
##title=
##
if REQUEST.has_key('Delete'):
    if not REQUEST.get('confirm_delete'):
        raise ValueError, ("You must check the 'confirm delete'"
                           " box to commit the deletion.")
    url = REQUEST.get('URL2') + '/FrontPage'

    # Try to get a parent url, so we can return there
    folder = context.aq_parent
    for p in context.parents:
        if hasattr(folder, p):
            url = folder[p].wiki_page_url()
            break

    context.delete()
    
elif REQUEST.has_key('Rename'):
    url = context.rename(REQUEST.get('new_id'))
    
RESPONSE.redirect('%s' % url)
