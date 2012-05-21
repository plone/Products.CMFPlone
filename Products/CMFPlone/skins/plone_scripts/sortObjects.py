## Script (Python) "sortObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contents, method='title_or_id'
##title=sorts and pre-filters objects


def get_sortable(o):
    val = getattr(o, method)()
    try:
        val = val.lower()
    except AttributeError:
        pass
    return val

aux = [(get_sortable(o), o) for o in contents]
aux.sort()
return [x[1] for x in aux]
