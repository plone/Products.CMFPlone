## Script (Python) "showEditableBorder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id
##title=returns whether or not current template displays *editable* border
##
REQUEST=context.REQUEST
membership=context.portal_membership

actions=context.portal_actions.listFilteredActionsFor(context)
anonymous=membership.isAnonymousUser()
contextEditable=membership.checkPermission('Modify portal content', context) 
isWorkflowable=actions.get('workflow', None)

if anonymous and not contextEditable:
    return 0

if template_id=='folder_contents' or isWorkflowable :
    return 1

if contextEditable and context.getTypeInfo().Type()=='Topic': return 1
