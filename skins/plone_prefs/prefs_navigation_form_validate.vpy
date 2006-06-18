from Products.CMFCore.utils import getToolByName

request = context.REQUEST

required = ('topLevel', 'bottomLevel')
intvals = ('topLevel', 'bottomLevel')

for k in required:
    v = request.form.get(k, '').strip()
    if not v:
        state.setError(k, 'Input is required but not given.')
for k in intvals:
    v = request.form.get(k, '').strip()
    if v:
        try:
            int(v)
        except ValueError:
            state.setError(k, 'Input must be an integer.')

root = request.form.get('root', None)
if root and root != '/':
    purl = getToolByName(context, 'portal_url')
    rootPath = purl.getPortalPath() + root
    rootObject = purl.getPortalObject().restrictedTraverse(rootPath)
    if rootObject is None:
        state.setError('root', 'Could not find %s' % root)

if state.getErrors():
    return state.set(status='failure',
        portal_status_message='Please correct the indicated errors.')
else:
    return state

