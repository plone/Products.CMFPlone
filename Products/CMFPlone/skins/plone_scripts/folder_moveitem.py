## Script (Python) "folder_setorder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=item_id,delta,subset_ids=None
##title=
##
try:
    delta = int(delta)
    if subset_ids is not None:
        position_id = [(context.getObjectPosition(id), id) for id in subset_ids]
        position_id.sort()
        if subset_ids != [id for position, id in position_id]:
            raise ValueError("Client/server ordering mismatch.")
    context.moveObjectsByDelta(item_id, delta, subset_ids)
except ValueError as e:
    context.REQUEST.response.setStatus('BadRequest')
    return str(e)

context.plone_utils.reindexOnReorder(context)
return "<done />"
