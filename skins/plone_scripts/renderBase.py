# returns correct base href
if getattr(context.aq_explicit, 'isPrincipiaFolderish', 0):
    return context.absolute_url()+'/'
else:
    path = '/'.join(context.portal_url.getRelativeContentPath(context)[:-1])
    appendix = ''
    if len(path) > 0:
        appendix = '/'
    return context.portal_url() + '/' + path + appendix
