# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("plone")

MTYPES_DISPLAY = {
    "info": {
        "msg": _("statusmessage_mtype_info", default="Info:"),
        "icon": "plone-statusmessage-info",
        "cssclass": "statusmessage statusmessage-info alert alert-info",
    },
    "warning": {
        "msg": _("statusmessage_mtype_warning", default="Warning:"),
        "icon": "plone-statusmessage-warning",
        "cssclass": "statusmessage statusmessage-warning alert alert-warning",
    },
    "error": {
        "msg": _("statusmessage_mtype_error", default="Error:"),
        "icon": "plone-statusmessage-error",
        "cssclass": "statusmessage statusmessage-error alert alert-danger",
    },
    "danger": {
        "msg": _("statusmessage_mtype_danger", default="Danger:"),
        "icon": "plone-statusmessage-danger",
        "cssclass": "statusmessage statusmessage-danger alert alert-danger",
    },
}


class GlobalStatusMessage(ViewletBase):
    """Display messages to the current user"""

    index = ViewPageTemplateFile("globalstatusmessage.pt")

    def update(self):
        super(GlobalStatusMessage, self).update()
        self.status = IStatusMessage(self.request)
        self.messages = self.status.show()

    def display_info_for_mtype(self, mtype):
        """get info for display of an mtype"""
        return MTYPES_DISPLAY.get(mtype, MTYPES_DISPLAY["info"])
