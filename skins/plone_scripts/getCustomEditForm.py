## Script (Python) "getCustomEditForm"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj
##title=
##
from string import join, split, lower
actions = None
custom_form = ''

if obj:
    contentType = join(split(lower(obj.Type())),'')
    custom_form = contentType+'_custom_form'
    actions = context.portal_actions.listFilteredActionsFor(obj)
    obj_actions = actions['object']

    if hasattr(context, custom_form):
        return obj.absolute_url()+'/'+custom_form

    for a in obj_actions:
        if a['name']=='Edit': return a['url']

    return obj.absolute_url()

raise Exception, 'custom edit form, edit form, and absolute_url could not be found'
