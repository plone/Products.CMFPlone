## Script (Python) "aboveInThread"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Discussion parent breadcrumbs
breadcrumbs = ''
crumbs = []
parents = context.parentsInThread()

if parents:
    for parent in parents:
        crumbs.append('<a href="%s">%s</a> ' % (parent.absolute_url(), parent.Title()))

    breadcrumbs = '<strong>&raquo;</strong> '.join(crumbs)

return breadcrumbs
