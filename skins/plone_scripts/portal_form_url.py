## Script (Python) "portal_form_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id,containerPath=None
##title=used to do URL mangling for portal_form
##

url = context.REQUEST.URLPATH0
url_list = url.split('/')

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
