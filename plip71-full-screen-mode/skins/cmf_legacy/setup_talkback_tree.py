## Script (Python) "setup_talkback_tree"
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
