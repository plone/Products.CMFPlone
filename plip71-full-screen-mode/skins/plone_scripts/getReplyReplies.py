## Script (Python) "getReplies"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj
##title=gets the replies to an object
##
replies = []
pd = container.portal_discussion

def getRs(obj, replies, counter):
    rs = pd.getDiscussionFor(obj).getReplies()
    rs = container.sort_modified_ascending(rs)
    for r in rs:
        replies.append({'depth':counter, 'object':r})
        getRs(r, replies, counter=counter + 1)

getRs(obj, replies, 0)
return replies
