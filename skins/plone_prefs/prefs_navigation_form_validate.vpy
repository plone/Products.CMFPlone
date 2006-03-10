
request = context.REQUEST

required = ('name', 'topLevel', 'bottomLevel')
intvals = ('topLevel', 'bottomLevel')

for k in required:
    v = request.form.get(k, '').strip()
    if not v:
        state.setError(k, 'Input Required.')
for k in intvals:
    v = request.form.get(k, '').strip()
    if v:
        try:
            int(v)
        except ValueError:
            state.setError(k, 'Input must be an integer.')

if state.getErrors():
    return state.set(status='failure',
        portal_status_message='Please correct the indicated errors.')
else:
    return state

