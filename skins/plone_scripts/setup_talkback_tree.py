## Script (Python) "setup_talkback_tree"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=tree_root
##title=Standard Tree
##
from ZTUtils import SimpleTreeMaker

tm = SimpleTreeMaker('tb_tree')
def getKids(object):
    return object.talkback.getReplies()
tm.setChildAccess(function=getKids)

tree, rows = tm.cookieTree(tree_root)
rows.pop(0)
return {'root': tree, 'rows': rows}
