# returns correct base href

from AccessControl import Unauthorized

# when accessing via WEBDAV you're not allowed to access aq_explicit
try:
    if getattr(context.aq_explicit, 'isPrincipiaFolderish', 0):
        return context.absolute_url() + '/'
    else:
        return context.absolute_url()
except Unauthorized:
    pass
