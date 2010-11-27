## Controller Python Script "folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=paths=[],new_ids=[],new_titles=[]
##title=Rename Objects
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
from Products.PythonScripts.standard import url_unquote

portal = context.portal_url.getPortalObject()
request = context.REQUEST

message = None
putils = context.plone_utils

orig_template = request.get('orig_template', None)
change_template = paths and orig_template is not None
if change_template:
    # We were called by 'object_rename'.  So now we take care that the
    # user is redirected to the object with the new id.
    portal = context.portal_url.getPortalObject()
    obj = portal.restrictedTraverse(paths[0])
    new_id = new_ids[0]
    obid = obj.getId()
    if new_id and new_id != obid:
        orig_path = obj.absolute_url_path()
        # replace the id in the object path with the new id
        base_path = orig_path.split('/')[:-1]
        base_path.append(new_id)
        new_path = '/'.join(base_path)
        orig_template = orig_template.replace(url_unquote(orig_path),
                                              new_path)
        request.set('orig_template', orig_template)
        message = _(u"Renamed '${oldid}' to '${newid}'.",
                    mapping={u'oldid' : obid, u'newid' : new_id})

success, failure = putils.renameObjectsByPaths(paths, new_ids, new_titles,
                                               REQUEST=request)

if message is None:
    message = _(u'${count} item(s) renamed.',
                mapping={u'count' : str(len(success))})

if failure:
    message = _(u'The following item(s) could not be renamed: ${items}.',
                mapping={u'items' : ', '.join(failure.keys())})

context.plone_utils.addPortalMessage(message)
return state
