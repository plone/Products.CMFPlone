## Script (Python) "require_login"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Login
##

request = context.REQUEST

# Handle external login requests from other portals where the user is already
# logged in in this portal
next = request.get('next', None)
if (next is not None and context.portal_url.isURLInPortal(next) 
    and not context.portal_membership.isAnonymousUser()):
    return context.restrictedTraverse('external_login_return')()

# Handle login on this portal where login is internal
site_properties = context.portal_properties.site_properties
external_login_url = site_properties.getProperty('external_login_url')
external_login_iframe = site_properties.getProperty('external_login_iframe')
if not external_login_url or external_login_iframe:
    return context.restrictedTraverse('login_form')()

# Handle login on this portal where login is external
next = request.URL1 + '/logged_in'
url = "%s?next=%s" % (external_login_url, next)
came_from = request.get('came_from')
if came_from:
    url = "%s&came_from=%s" % (url, came_from)
request.RESPONSE.redirect(url)
