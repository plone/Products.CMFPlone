## Script (Python) "getStateClassName"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=wf_state=None
##title=Returns a coocked state class name for css usage
##
result = ""
if wf_state:
    result = "state-" + wf_state.replace(' ', '-')
else:
    result = ""

return result
