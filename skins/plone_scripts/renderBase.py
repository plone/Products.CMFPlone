# returns correct base href
if getattr(context.aq_explicit, 'isPrincipiaFolderish', 0):
    return context.absolute_url()+'/'
else:
    return context.absolute_url()
