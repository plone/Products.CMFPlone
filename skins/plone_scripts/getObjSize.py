## Script (Python) "getObjSize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj,size=''
##title=
##

# allow arbitrary sizes to be passed through,
# if there is no size, but there is an object
# look up the object, this maintains backwards 
# compatibility
if not size and obj and hasattr(obj, 'get_size'):
    size=obj.get_size()

# if the size is a float, then make it an int
# happens for large files
try:
    size = int(size)
except (ValueError, TypeError):
    pass

if same_type(size, 0):
    if size<1024:
        return '1 K'
    elif size>1048576:
        return '%.02f M' % float(size/1048576.0)
    else:
        return str(int(size)/1024)+' K'

return size
