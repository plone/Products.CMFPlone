## Controller Python Script "createObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=None,type_name=None,script_id=None
##title=
##

from DateTime import DateTime
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
REQUEST=context.REQUEST
response = REQUEST.response
response.setHeader('Expires', 'Sat, 01 Jan 2000 00:00:00 GMT')
response.setHeader('Cache-Control', 'no-cache')

if id is None:
    id=context.generateUniqueId(type_name)

if type_name is None:
    raise Exception, 'Type name not specified'

types_tool = getToolByName(context, 'portal_types')

fti = types_tool.getTypeInfo(type_name)
if fti is None:
    raise KeyError("Type name not found: %s." % type_name)

if not fti.queryMethodID('edit'):
    state.setStatus('success_no_edit')

if type_name in context.portal_factory.getFactoryTypes():
    new_url = 'portal_factory/' + type_name + '/' + id
    if state.getStatus() != 'success_no_edit':
        new_url = new_url + '/edit'
    state.set(status='factory', next_action='redirect_to:string:%s'%new_url)
    # If there's an issue with object creation, let the factory handle it
    return state
else:
    new_id = context.invokeFactory(id=id, type_name=type_name)
    if new_id is None or new_id == '':
       new_id = id
    o=getattr(context, new_id, None)
    tname = o.getTypeInfo().Title()
    message = _(u'${tname} has been created.', mapping={u'tname' : tname})
    transaction_note('Created %s with id %s in %s' % (o.getTypeInfo().getId(), new_id, context.absolute_url()))

if o is None:
    raise Exception

if script_id:
    state.setId(script_id)

if message:
    context.plone_utils.addPortalMessage(message)
return state.set(context=o)
