# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage


class GlobalStatusMessage(ViewletBase):
    """Display messages to the current user"""

    index = ViewPageTemplateFile('globalstatusmessage.pt')

    def update(self):
        super(GlobalStatusMessage, self).update()
        self.status = IStatusMessage(self.request)
        self.messages = self.status.show()
