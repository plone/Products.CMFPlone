## Script (Python) "selectedTabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default_tab, obj=None, portal_tabs=[]
##title=
##

from AccessControl import Unauthorized

# we want to centalize where all tab selection is done
# for now e will start off with the top tabs, 'portal_tabs'
url_tool = context.portal_url
plone_url = url_tool()
valid_actions = []
if obj is None:
    obj = context

try:
    contentpath=url_tool.getRelativeContentPath(obj)
except (Unauthorized, IndexError):
    pass

if contentpath:
    path = '/' + '/'.join(contentpath)
    for action in portal_tabs:
        action_path = action['url'].replace(plone_url,'')
        if not action_path.startswith('/'):
            action_path = '/' + action_path
        if path.startswith(action_path):
            # Make a list of the action ids, along with the path length for
            # choosing the longest (most relevant) path.
            valid_actions.append((len(action_path), action['id']))

# Sort by path length, the longest matching path wins
valid_actions.sort()
if valid_actions:
    return {'portal':valid_actions[-1][1]}

return {'portal':default_tab}
