## Script (Python) "getWorkflowHistory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return the workflow history for an object
##

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import log

history = []

# check if the current user has the proper permissions
if context.portal_membership.checkPermission('Modify portal content', context):

    try:
        # get total history
        review_history =context.portal_workflow.getInfoFor(context, 'review_history')

        # filter out the irrelevant stuff
        review_history = [r for r in review_history if r['action']]

        #reverse the list
        history = context.reverseList(review_history)

    except WorkflowException:
        log( 'CMFPlone/skins/plone_scripts/getWorkflowHistory: '
             '%s has no associated workflow' % context.absolute_url() )

return history
