## Script (Python) "filterCookie.py $Revision$"
##parameters=
##title=Manage filter cookie
##
REQUEST=context.REQUEST
if REQUEST.get('clear_view_filter', 0):
    context.clearCookie()
    REQUEST.set('folderfilter', '')
    REQUEST.set('close_filter_form', '1')
elif REQUEST.get('set_view_filter', 0):
    filter=context.encodeFolderFilter(REQUEST)
    REQUEST.RESPONSE.setCookie('folderfilter', filter, path='/',
                                expires='Wed, 19 Feb 2020 14:28:00 GMT')
    REQUEST.set('folderfilter', '%s' % filter)
