from Products.Five.browser import BrowserView

class LoginAlias(BrowserView):
    """Base class for views that perform a redirect
    """
    
    def redirect(self):
        url = self.request.get('HTTP_REFERER', None)
        if not url:
            url = self.context.absolute_url()
        self.request.response.redirect('login_form?came_from=%s' % url)
