## Script (Python) "getBatchPageCounts"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=source, batch
##title=
##
total = len(source)
b_size = batch.size
cur_page = 0
no_pages = float(total)/b_size
if b_size%total: no_pages=no_pages+1


return (cur_page, no_pages)
