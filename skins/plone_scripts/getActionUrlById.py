## Script (Python) "getActionUrlById"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=action_id, actions
##title=given object actions and a action_id return the url
##

for action in actions:
   if action.get('id', None)==action_id \
      or action.get('name', '').lower()==action_id:
      return action.get('url', None)

