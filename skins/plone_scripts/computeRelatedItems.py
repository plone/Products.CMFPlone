## Script (Python) "computeRelatedItems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=find related items for an object
##

if hasattr(context, 'getRelatedItems'):
    outgoing = context.getRelatedItems()
    incoming = []
    # if you want to show up the items which point to this one, too, then use the
    # line below
    #incoming = context.getBRefs('relatesTo') 
    res = []
    mtool = context.portal_membership
    
    for d in outgoing+incoming:
        if d not in res:
            if mtool.checkPermission('View', d):
                res.append(d)
    
    return res





