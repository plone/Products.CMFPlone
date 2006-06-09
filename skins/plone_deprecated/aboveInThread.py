## Script (Python) "aboveInThread"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Discussion parent breadcrumbs
context.plone_log("The aboveInThread script is deprecated and will be "
                  "removed in plone 3.5.")
breadcrumbs = ''
crumbs = []
parents = context.parentsInThread()

if parents:
    for parent in parents:
        crumbs.append('<a href="%s">%s</a> ' % (parent.absolute_url(), putils.pretty_title_or_id(parent)))

    breadcrumbs = '<strong>&raquo;</strong> '.join(crumbs)

return breadcrumbs
