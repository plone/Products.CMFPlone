from DateTime import DateTime
from plone.base import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_nativestring
from Products.Five import BrowserView

import plone.api as api


class ErrorLogUpdate(BrowserView):
    def __call__(self):
        member = api.user.get_current()

        if getattr(self.request, "form.button.search", None) is not None:
            search = self.request.form.get("search_entry")
            if search == "":
                member.setProperties(error_log_update=0.0)
                self.context.plone_utils.addPortalMessage(_("Showing all entries"))
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url() + "/@@error-log-form"
                )
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + "/@@error-log-show-entry?id=%s" % search
            )

        elif getattr(self.request, "form.button.showall", None) is not None:
            member.setProperties(error_log_update=0.0)
            self.context.plone_utils.addPortalMessage(_("Showing all entries"))
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + "/@@error-log-form"
            )

        elif getattr(self.request, "form.button.clear", None) is not None:
            member.setProperties(error_log_update=DateTime().timeTime())
            self.context.plone_utils.addPortalMessage(_("Entries cleared"))
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + "/@@error-log-form"
            )

        else:
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + "/@@error-log-form"
            )


class ErrorLogSetProperties(BrowserView):
    def __call__(self):
        keep_entries = self.request.form.get("keep_entries")
        ignored_exceptions = self.request.form.get("ignored_exceptions")
        copy_to_zlog = self.request.form.get("copy_to_zlog", 0)

        ignored_exceptions = map(safe_nativestring, ignored_exceptions)
        self.context.error_log.setProperties(
            keep_entries, copy_to_zlog, ignored_exceptions
        )
        self.context.plone_utils.addPortalMessage(_("Changes made."))

        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + "/@@error-log-form"
        )
