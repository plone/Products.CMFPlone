## Script (Python) "portal_form_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id,protocol=None
##title=used to do URL mangling for portal_form
#
# portal_form_url is a convenience method that inserts 'portal_form' in the
#   appropriate place in your URL if it's not already there.  It isn't foolproof
#   so in some weird cases
# template_id - The id of the template from which portal_form_url was called
# protocol - Lets you specify that the resulting URL must be http, https, etc.
#            If protocol is not specified, uses the same protocol as the URL
#            from which it was invoked

url = context.REQUEST.URL0
url_list = url.split('/')

if protocol:
    url_list[0] = protocol + ':'

found = -1
i = 0
for d in url_list:
    if d == 'portal_form':
        found = i
        break
    i = i + 1
if found > 0:
    if len(url_list) > found+1:
        url_list = url_list[:found+2]
        url_list[found+1] = template_id
    else:
        url_list.append(template_id)
else:
    if url_list[-1] != template_id:
        url_list.append(template_id)
    url_list.insert(len(url_list)-1, 'portal_form')
return string.join(url_list,'/')
