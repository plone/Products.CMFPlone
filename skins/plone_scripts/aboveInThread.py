## Script (Python) "aboveInThread"

##bind container=container

##bind context=context

##bind namespace=

##bind script=script

##bind subpath=traverse_subpath

##parameters=

##title=Discussion parent breadcrumbs



breadcrumbs = ''

parents = context.parentsInThread()



if parents:

    breadcrumbs = ''

    for parent in parents:

        p_str = '<a href="%s">%s</a> <strong>&raquo;</strong> ' % (parent.absolute_url(), parent.Title())

        breadcrumbs = breadcrumbs + p_str



    breadcrumbs = breadcrumbs[:-1] + '<p>'

        

return breadcrumbs



