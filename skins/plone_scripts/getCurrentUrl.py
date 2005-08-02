## Script (Python) "getCurrentUrl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return the current full URL including query string
##
request = context.REQUEST
url = request.get('ACTUAL_URL', request.get('URL', None))
query = request.get('QUERY_STRING','')
if query:
    query = '?'+query
return url+query
