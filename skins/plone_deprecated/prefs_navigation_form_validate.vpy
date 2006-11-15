from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

request = context.REQUEST

required = ('topLevel', 'bottomLevel')
intvals = ('topLevel', 'bottomLevel')

for k in required:
    v = request.form.get(k, '').strip()
    if not v:
        state.setError(k, _(u'Input is required but not given.'))
for k in intvals:
    v = request.form.get(k, '').strip()
    if v:
        try:
            int(v)
        except ValueError:
            state.setError(k, _(u'Input must be an integer.'))

root = request.form.get('root', None)
if root and root != '/':
    purl = getToolByName(context, 'portal_url')
    rootPath = purl.getPortalPath() + root
    rootObject = purl.getPortalObject().restrictedTraverse(rootPath)
    if rootObject is None:
        state.setError('root', _(u'Could not find ${root}', mapping={u'root' : root}))

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'))
    return state.set(status='failure')
else:
    return state

