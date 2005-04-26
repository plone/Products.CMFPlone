## Script (Python) "selectedTabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default_tab, obj=None
##title=
##

from AccessControl import Unauthorized

# we want to centalize where all tab selection is done
# for now e will start off with the top tabs, 'portal_tabs'
if obj is None:
    obj = context

try:
    contentpath=context.portal_url.getRelativeContentPath(obj)
    if contentpath:
        return {'portal':contentpath[0]}
except (Unauthorized, IndexError):
    pass

return {'portal':default_tab}
