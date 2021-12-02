import plone.api as api
from DateTime import DateTime
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_nativestring
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PrefsErrorLogForm(BrowserView):

    template = ViewPageTemplateFile('prefs_error_log_form.pt')

    def __call__(self):
        return self.template(self)


class PrefsErrorLogShowEntry(BrowserView):

    template = ViewPageTemplateFile('prefs_error_log_showEntry.pt')

    def __call__(self):
        return self.template(self)


class PrefsErrorLogUpdate(BrowserView):

    def __call__(self):
        member = api.user.get_current()

        if getattr(self.request, 'form.button.search', None) is not None:
            search = self.request.form.get('search_entry')
            if search == '':
                member.setProperties(error_log_update=0.0)
                self.context.plone_utils.addPortalMessage(_('Showing all entries'))
                return self.request.RESPONSE.redirect(self.context.absolute_url() + '/prefs_error_log_form')
            return self.request.RESPONSE.redirect(self.context.absolute_url() + '/prefs_error_log_showEntry?id=%s' % search)

        elif getattr(self.request, 'form.button.showall', None) is not None:
            member.setProperties(error_log_update=0.0)
            self.context.plone_utils.addPortalMessage(_('Showing all entries'))
            return self.request.RESPONSE.redirect(self.context.absolute_url() + '/prefs_error_log_form')

        elif getattr(self.request, 'form.button.clear', None) is not None:
            member.setProperties(error_log_update=DateTime().timeTime())
            self.context.plone_utils.addPortalMessage(_('Entries cleared'))
            return self.request.RESPONSE.redirect(self.context.absolute_url() + '/prefs_error_log_form')

        else:
            return self.request.RESPONSE.redirect(self.context.absolute_url() + '/prefs_error_log_form')


class PrefsErrorLogSetProperties(BrowserView):

    def __call__(self):
        keep_entries = self.request.form.get('keep_entries')
        ignored_exceptions = self.request.form.get('ignored_exceptions')
        copy_to_zlog = self.request.form.get('copy_to_zlog', 0)

        ignored_exceptions = map(safe_nativestring, ignored_exceptions)
        self.context.error_log.setProperties(keep_entries, copy_to_zlog, ignored_exceptions)
        self.context.plone_utils.addPortalMessage(_('Changes made.'))

        return self.request.RESPONSE.redirect(self.context.absolute_url() + '/prefs_error_log_form')
