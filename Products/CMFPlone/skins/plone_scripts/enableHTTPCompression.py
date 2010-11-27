## Script (Python) "enableHTTPCompression"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=request=None, force=0, debug=0, enable=0
##title=Enable zlib based HTTP compression

# force: force http compression even if the browser doesn't send an accept
# debug: return compression state (0: no, 1: yes, 2: force)

if not enable:
    if debug:
        return '<!-- compression status: disabled -->'
    else:
        return

if request is None:
    request = context.REQUEST

result = request.RESPONSE.enableHTTPCompression(REQUEST=request, force=force)

if debug:
    return '<!-- compression status: %s -->' % result
