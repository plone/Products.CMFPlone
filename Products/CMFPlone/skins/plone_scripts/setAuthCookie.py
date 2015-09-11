## Script (Python) "setAuthCookie"
##title=Set Authentication Cookie
##parameters=resp, cookie_name, cookie_value

try:
    length = context.portal_registry['plone.auth_cookie_length']
except AttributeError:
    length = 0

try:
    length = int(length)
except ValueError:
    length = 0

cookie_path = '/'
if length:
    expires = (DateTime() + length).toZone('GMT').rfc822()
    resp.setCookie(
        cookie_name,
        cookie_value,
        path=cookie_path,
        expires=expires)
else:
    resp.setCookie(cookie_name, cookie_value, path=cookie_path)
