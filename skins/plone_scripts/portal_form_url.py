## Script (Python) "portal_form_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id
##title=used to do URL mangling for portal_form
##

url = context.REQUEST.URLPATH0

if url.find('portal_form') != -1:
    return url

url_list = url.split('/')
if url_list[-1] != template_id:
    url_list.append(template_id)
url_list.insert(len(url_list)-1, 'portal_form')
return string.join(url_list,'/')
