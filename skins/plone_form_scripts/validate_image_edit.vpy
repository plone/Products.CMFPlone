## Controller Python Script "validate_image_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates image_edit_form contents
##

validator = context.portal_form.createForm()
validator.addField('title', 'String', required=0)
errors = validator.validate(context.REQUEST)
for fieldid, error in errors.items():
    state.setError(fieldid, error)

filename=getattr(context.REQUEST['file'], 'filename', None)
size = 0
if hasattr(context, 'get_size'):  # make sure things work with portal_factory
    size=context.get_size()
if not filename and not size:
    state.setError('file', 'You must upload a file')

if context.CreationDate() == context.ModificationDate() and filename:
    alternative_id = filename[max( string.rfind(filename, '/')
                       , string.rfind(filename, '\\')
                       , string.rfind(filename, ':') )+1:].strip()
else:
    alternative_id = context.getId()

id = context.REQUEST.get('id', '').strip()
id_err = context.check_id(id, 1, alternative_id)
if id_err:
    state.setError('id', id_err)


if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
