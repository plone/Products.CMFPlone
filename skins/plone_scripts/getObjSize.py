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

const = {'kB':1024,
         'MB':1024*1024,
         'GB':1024*1024*1024}
order = ('GB', 'MB', 'kB')
smaller = order[-1]

if hasattr(obj, 'get_size'):
    size = obj.get_size()

    if not size:
        return '0 %s' % smaller

    # if the size is a float, then make it an int
    # happens for large files
    try:
        size = int(size)
    except (ValueError, TypeError):
        pass

    if same_type(size, 0) or same_type(size, 0L):
        if size < const[smaller]:
            return '1 %s' % smaller
        for c in order:
            if size/const[c] > 0:
                break
        return '%.1f %s' % (float(size/float(const[c])), c)

return size
