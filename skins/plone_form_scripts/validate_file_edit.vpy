## Controller Python Script "validate_file_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id='',file=None
##title=Validates file_edit_form contents
##

from Products.CMFPlone import PloneMessageFactory as _

size = 0
id_from_file = 0
id = id.strip()

if file is None:
    filename=None
else:
    filename=getattr(file, 'filename', None)

if hasattr(context, 'get_size'):  # make sure things work with portal_factory
    size=context.get_size()

if not filename and not size:
    state.setError('file', _(u'You must upload a file'))

if context.CreationDate() == context.ModificationDate() and filename:
    alternative_id = filename[max( string.rfind(filename, '/')
                       , string.rfind(filename, '\\')
                       , string.rfind(filename, ':') )+1:].strip()
    if not id:
        id_from_file = 1
else:
    alternative_id = context.getId()

id_err = context.check_id(id, 1, alternative_id)
if id_err:
    state.setError(id_from_file and 'file' or 'id', id_err)

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
