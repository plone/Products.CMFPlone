def getObjectSource(self, template_id=''):
    template = getattr(self, template_id, None)
    if template:
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/plain')
        if hasattr(template, '_text'):
            return template._text
        if hasattr(template, 'document_src'): #dtml
            return template.document_src
    return 'source could not be rendered'
