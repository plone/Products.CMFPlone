from plone.app.layout.viewlets.common import ViewletBase


class HTTPCachingHeaders(ViewletBase):
    """Replace the old global_cache_settings/macros/cacheheaders
    """
    def index(self):
        return u""

    def update(self):
        super(HTTPCachingHeaders, self).update()
        self.setHeader = self.request.response.setHeader
        self.set_content_type()
        self.set_language()
        self.set_expires()

    def enable_compression(self):
        """Call to activate gzip"""
        self.context.enableHTTPCompression(request=request, enable=1)

    def set_content_type(self):
        self.setHeader('Content-Type', 'text/html;;charset=utf-8')

    def set_language(self):
        self.lang = getattr(self.context, 'Language', None)
        self.lang = self.lang or self.portal_state.default_language()
        self.setHeader('Content-Language', self.lang)

    def set_expires(self):
        self.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')

"""
The is the original macro global_cache_settings/macros/cacheheaders
<metal:cacheheaders define-macro="cacheheaders"
    tal:define="portal_state context/@@plone_portal_state;
                lang context/Language|nothing;
                lang python: lang or portal_state.default_language();
                setHeader python:request.RESPONSE.setHeader;">
    <metal:block tal:define="dummy python:setHeader('Content-Type', 'text/html;;charset=utf-8')" />
    <metal:block tal:define="dummy python:setHeader('Content-Language', lang)" />
    <metal:block tal:define="dummy python:setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')" />
    <tal:gzip tal:replace="nothing">
      Use the following line to enable gzip compression
      tal:content="structure python:context.enableHTTPCompression(request=request, enable=1)"
    </tal:gzip>
</metal:cacheheaders>

"""