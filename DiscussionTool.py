from Products.CMFDefault.DiscussionTool import DiscussionTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore.utils import format_stx
from DocumentTemplate.DT_Util import html_quote

class DiscussionTool(BaseTool):

    meta_type = ToolNames.DiscussionTool
    security = ClassSecurityInfo()

    security.declareProtected('Modify portal content', 'cookContent')
    def cookReply(self, reply, text_format=None):
        """ XXX We need this because currently we can not easily change the
            text_format on Documetn objects.  Discussions in plone are going
            to use plain-text for now.  stx is too confusing.
        """
        level = reply._stx_level
        text = reply.text

        if text_format is None:
            text_format=reply.text_format

        if text_format == 'html':
            reply.text = reply.cooked_text = text
        elif text_format == 'plain':
            reply.text = text
            reply.cooked_text = html_quote(text).replace('\n','<br>')
        else:
            reply.cooked_text = format_stx(text=text, level=level)
            reply.text = text

DiscussionTool.__doc__ = BaseTool.__doc__

InitializeClass(DiscussionTool)
