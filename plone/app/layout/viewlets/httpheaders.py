from plone.app.layout.viewlets.common import ViewletBase


class HeaderViewlet(ViewletBase):
    """a base viewlet that do not render anything, just ready to set headers"""

    def index(self):
        return u""

    def update(self):
        super(HeaderViewlet, self).update()
        self.setHeader = self.request.response.setHeader
        for name, value in self.getHeaders():
            self.setHeader(name, value)

    def getHeaders(self):
        return []


class HTTPCachingHeaders(HeaderViewlet):
    """Replace the old global_cache_settings/macros/cacheheaders
    """

    def enable_compression(self):
        """Call to activate gzip"""
        self.context.enableHTTPCompression(request=request, enable=1)

    def getHeaders(self):
        self.lang = getattr(self.context, 'Language', None)
        self.lang = self.lang or self.portal_state.default_language()
        return [
            ('Content-Type', 'text/html;;charset=utf-8'),
            ('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT'),
            ('Content-Language', self.lang)
        ]


class XUACompatible(HeaderViewlet):
    """set the header ('X-UA-Compatible', 'IE=edge,chrome=1');"""

    def getHeaders(self):
        return [('X-UA-Compatible', 'IE=edge,chrome=1')]
