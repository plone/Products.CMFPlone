# -*- coding: utf-8 -*-
##parameters=

if context.portal_membership.isAnonymousUser():
    return []

return context.portal_workflow.getWorklistsResults()
