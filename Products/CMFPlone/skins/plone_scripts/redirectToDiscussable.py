## Script (Python) "redirectToDiscussable"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Redirect from a discussionItem to it's absolute parent (discussable object)

from Products.CMFCore.utils import getToolByName

if context.portal_type == 'Discussion Item':
    pu = getToolByName(context, "plone_utils")
    redirect_target = pu.getDiscussionThread(context)[0]
    state = redirect_target.restrictedTraverse("@@plone_context_state")

    context.REQUEST.response.redirect(state.view_url() + '#' + context.id)
