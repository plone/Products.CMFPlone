## Script (Python) "expireAuthCookie"
##title=Expire Authentication Cookie
##parameters=resp, cookie_name
resp.expireCookie( cookie_name, path='/')
resp.expireCookie( '__ac', path='/')
context.plone_log('expired __ac and ' + cookie_name)
