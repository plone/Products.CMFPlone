## Script (Python) "filterCookie"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Manage filter cookie
##
context.plone_log("The filterCookie script is deprecated and will be "
                  "removed in plone 3.0.")
REQUEST=context.REQUEST

if REQUEST.get('filter_state', 0):
    REQUEST.set(REQUEST['filter_state'], 1)

#path = context.portal_url.getPortalPath()

if REQUEST.get('clear_view_filter', 0):
    REQUEST.RESPONSE.expireCookie('folderfilter', path='/')
    REQUEST.set('portal_status_message', 'Filter cleared.')
    REQUEST.set('folderfilter', '')
    REQUEST.set('close_filter_form', '1')
    return
elif REQUEST.get('set_view_filter', 0):
    filter=context.encodeFolderFilter(REQUEST)
    REQUEST.RESPONSE.setCookie('folderfilter', filter, path='/',
                               expires='Wed, 19 Feb 2020 14:28:00 GMT')
    REQUEST.set('folderfilter', filter)
    REQUEST.set('portal_status_message',
                'Filtered by %s.' % ' '.join(REQUEST['filter_by_portal_type']) )
