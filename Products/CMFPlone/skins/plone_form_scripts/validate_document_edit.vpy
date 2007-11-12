## Controller Python Script "validate_document_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id='',file=''
##title=Validates a document edit_form contents
##

from Products.CMFPlone import PloneMessageFactory as _

filename = getattr(file, 'filename' ,'')
if file and filename:
    file.seek(0)
    headers = file.headers
    if headers.get('Content-Type', 'text/plain').find('text')==-1:
        state.setError('file', _(u'This file is not text. To upload binary files create File content.'))

if context.CreationDate() == context.ModificationDate() and filename:
    alternative_id = filename[max( string.rfind(filename, '/')
                       , string.rfind(filename, '\\')
                       , string.rfind(filename, ':') )+1:].strip()
else:
    alternative_id = context.getId()

id=id.strip()
id_err = context.check_id(id, 1, alternative_id)
if id_err:
    state.setError('id', id_err)

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
