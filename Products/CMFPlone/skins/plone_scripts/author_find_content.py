## Script (Python) "author_find_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=author,limit_per_type=5,path=None
##title=Find content created by a specific author
##

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot

catalog = getToolByName(context, 'portal_catalog')
utils = getToolByName(context, 'plone_utils')

friendly_types = utils.getUserFriendlyTypes()

found   = {}
if path is None:
    path = getNavigationRoot(context)

content = catalog.searchResults(dict(
    Creator=author,
    portal_type=friendly_types,
    sort_on='modified',
    sort_order='reverse',
    path=path))

for item in content:
    itemType = item.portal_type

    if not itemType in found:
        found[itemType] = []
    if len(found[itemType]) < limit_per_type:
        found[itemType].append(item)

## The end result is a dictionary of lists, where the keys are the actual
## portal types. This means they are in rather random order..

types = found.keys()
types.sort()

results = []

for t in types:
    results.append({'portal_type' : t, 'content_items' : found[t]})

return results

