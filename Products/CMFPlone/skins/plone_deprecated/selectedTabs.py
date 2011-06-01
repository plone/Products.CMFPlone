## Script (Python) "selectedTabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default_tab, obj=None, portal_tabs=[]
##title=
##
from zExceptions import Forbidden
if container.REQUEST.get('PUBLISHED') is script:
   raise Forbidden('Script may not be published.')

from AccessControl import Unauthorized

# we want to centralize where all tab selection is done
# for now we will start off with the top tabs, 'portal_tabs'
url_tool = context.portal_url
plone_url = url_tool()
request = context.REQUEST
valid_actions = []

url = request['URL']
path = url[len(plone_url):]

for action in portal_tabs:
    if not action['url'].startswith(plone_url):
        # In this case the action url is an external link. Then, we avoid
        # issues (bad portal_tab selection) continuing with next action.
        continue
    action_path = action['url'][len(plone_url):]
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
