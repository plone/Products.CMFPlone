from Products.CMFDefault.DiscussionTool import DiscussionTool as BaseTool
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFDefault.permissions import ReplyToItem

from plone.intelligenttext.transforms \
    import convertWebIntelligentPlainTextToHtml


class DiscussionTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Discussion Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/discussionitem_icon.png'

    security.declareProtected(ReplyToItem, 'cookReply')
    def cookReply(self, reply, text_format=None):
        """ TODO We need this because currently we can not easily change the
            text_format on document objects.  Discussions in plone are going
            to use plain-text for now.  stx is too confusing.
        """
        reply.cooked_text = convertWebIntelligentPlainTextToHtml(reply.text)

DiscussionTool.__doc__ = BaseTool.__doc__

InitializeClass(DiscussionTool)
