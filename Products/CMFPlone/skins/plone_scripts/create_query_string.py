## Script (Python) "create_query_string"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=qs=None, **kw
##title=Creates a query string based on existing string plus keyword arguments

from zExceptions import Forbidden
if container.REQUEST.get('PUBLISHED') is script:
    raise Forbidden('Script may not be published.')

from Products.PythonScripts.standard import url_quote_plus

L = []

if qs:
    # break an existing query string into key value pairs
    entityparts = qs.split('&amp;')
    for entitypart in entityparts:
        ampparts = entitypart.split('&')
        for amppart in ampparts:
            tmp = amppart.split('=', 1)
            if len(tmp) > 1:
                k, v = tmp
            else:
                k, v = tmp[0], ''
            L.append((k, v))
else:
    for k, v in kw.items():
        L.append((k, url_quote_plus(v)))

# separate k/v pairs with &amp; (dont blame me, see the RFC)
new = '&amp;'.join(['%s=%s' % (k, v) for k, v in L])
return new
