## Script (Python) "aboveInThread"
##parameters=
##title=Discussion parent breadcrumbs

breadcrumbs = ''
parents = context.parentsInThread()

if parents:
    breadcrumbs = 'Above in this comment thread: <br />'
    for parent in parents:
        p_str = '<a href="%s">%s</a> <br />' % (parent.absolute_url(), parent.Title())
        breadcrumbs = breadcrumbs + p_str + '&nbsp;&nbsp;'

    breadcrumbs = breadcrumbs[:-1] + '<p>'
        
return breadcrumbs

