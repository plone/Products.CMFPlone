#from zope.interface import implements
from Products.Five.browser import BrowserView

class Redirect(BrowserView):
#    implements(IRedirector)
    
    def __call__(self):
        dest = self.request.get('dest')
        if dest.startswith('http://'):
            return self.request.RESPONSE.redirect(dest)
        else:
            url = '%s/%s' % (self.context.absolute_url(), dest)
            return self.request.RESPONSE.redirect(url)
