from logging import getLogger
from Products.Five.browser import BrowserView

class FolderLocalroleFormAlias(BrowserView):
    """Base class for views that perform a redirect
    """
    
    def redirect(self):
        
        log = getLogger('Plone')
        log.warn("folder_localrole_form is deprecated and will be removed in "
                 "Plone 4.0. Use the /@@sharing view instead. Most likely, "
                 "if you see this message the old template is being "
                 "referenced in portal_types.")
        
        self.request.response.redirect('%s/@@sharing' % self.context.absolute_url())
