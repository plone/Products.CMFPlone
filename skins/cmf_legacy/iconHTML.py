## Script (Python) "iconHTML"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##title=Returns the HTML for the current object's icon, if it is available
##parameters=

# dont you just wish namespaces had a get(name,default) method?! ;-)
try:
    iconURL=context.getIcon()
except KeyError:
    try:
        iconURL=_['icon']
    except:
        iconURL=''

if iconURL:
    try:
        Type = context.Type()
    except:
        Type=''
    return '<img src="%s" align="left" alt="%s" border="0"/>' % (iconURL,
                                                                 Type)

return ''
