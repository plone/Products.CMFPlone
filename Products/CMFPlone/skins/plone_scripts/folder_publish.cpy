## Controller Python Script "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, paths=[], comment='No comment', expiration_date=None, effective_date=None, include_children=False
##title=Publish objects from a folder
##

from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

plone_utils=context.plone_utils
REQUEST=context.REQUEST
workflow = context.portal_workflow
content_status_modify=context.content_status_modify
failed = {}
success = {}

if workflow_action is None:
    context.plone_utils.addPortalMessage(_(u'You must select a publishing action.'), 'error')
    return state.set(status='failure')
if not paths:
    context.plone_utils.addPortalMessage(_(u'You must select content to change.'), 'error')
    return state.set(status='failure')

objs = context.getObjectsFromPathList(paths)

for o in objs:
    obj_path = '/'.join(o.getPhysicalPath())
    try:
        if o.isPrincipiaFolderish and include_children:
            
            # call the script to do the workflow action
            # catch it if there is not workflow action for this object
            # but continue with subobjects.
            # Since we can have mixed portal_type objects it can occur
            # quite easily that the workflow_action doesn't work for some objects
            # but we need to keep on going.
            try:
                o.content_status_modify( workflow_action,
                                         comment,
                                         effective_date=effective_date,
                                         expiration_date=expiration_date )
            except ConflictError:
                raise
            except Exception, e:
                # skip this object but continue with sub-objects.
                failed[obj_path]=e

            subobject_paths = ["%s/%s" % ('/'.join(o.getPhysicalPath()), id) for id in o.objectIds()]
            # Only call folder_publish on non empty folders
            if subobject_paths:
                o.folder_publish( workflow_action, 
                                  subobject_paths, 
                                  comment=comment, 
                                  include_children=include_children, 
                                  effective_date=effective_date,
                                  expiration_date=expiration_date )
        else:
            o.content_status_modify( workflow_action,
                                     comment,
                                     effective_date=effective_date,
                                     expiration_date=expiration_date )
                                     
            success[obj_path]=comment
    except ConflictError:
        raise
    except Exception, e:
        failed[obj_path]=e

transaction_note( str(paths) + ' transitioned ' + workflow_action )

# It is necessary to set the context to override context from content_status_modify
context.plone_utils.addPortalMessage(_(u'Item state changed.'))
return state.set(context=context)
