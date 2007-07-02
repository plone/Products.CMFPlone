from ZPublisher.HTTPResponse import HTTPResponse

# XXX This patch can be removed once we require Zope 2.10.4 and it is released.

def fixedGetHeader(self, name, literal=0):
    '''\
    Get a header value

    Returns the value associated with a HTTP return header, or
    "None" if no such header has been set in the response
    yet.

    As the setHeader method automatically lowercases all keys, we should return
    both exact as well as lowercased matches. We also provide the same literal
    mode that the setHeader method supports.
    '''
    result = self.headers.get(name, None)
    if literal:
        return result
    if result is None:
        result = self.headers.get(name.lower(), None)
    return result


HTTPResponse.getHeader = fixedGetHeader
