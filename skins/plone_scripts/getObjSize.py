## Script (Python) "getObjSize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj
##title=
##
size=''

try:
    if hasattr(obj, 'get_size'): 
        size=obj.get_size()

    if size:
        if size<1024:
            return '1 K'
        elif size>1048576:
            return '%.02f M' % float(size/1048576.0)
        else:
            return str(int(size)/1024)+' K'

except:
     return size

return size
