from .interfaces import IAuthorFeedbackForm
from AccessControl import Unauthorized
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import ISecuritySchema
from plone.base.interfaces.controlpanel import IMailSchema
from plone.base.utils import pretty_title_or_id
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.MailHost.interfaces import IMailHost
from Products.statusmessages.interfaces import IStatusMessage
from urllib.parse import quote_plus
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging


logger = logging.getLogger("Plone")


class AuthorFeedbackForm(form.Form):
    fields = field.Fields(IAuthorFeedbackForm)
    ignoreContext = True

    @button.buttonAndHandler(_("label_send", default="Send"), name="send")
    def handle_send(self, action):
        self.portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )

        self.portal = self.portal_state.portal()
        self.membership_tool = getToolByName(self.context, "portal_membership")

        self.feedback_template = self.context.restrictedTraverse(
            "@@author-feedback-template"
        )

        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).addStatusMessage(
                self.formErrorsMessage, type="error"
            )

            return

        referer = data.get("referer", "unknown referer")
        subject = data.get("subject", "")
        message = data.get("message", "")
        # Author is None means portal administrator
        author = data.get("author", None)

        sender = self.portal_state.member()
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        envelope_from = mail_settings.email_from_address

        if author is None:
            send_to_address = mail_settings.email_from_address
        else:
            author_member = self.membership_tool.getMemberById(author)
            send_to_address = author_member.getProperty("email")

        send_from_address = sender.getProperty("email")

        if send_from_address == "":
            IStatusMessage(self.request).addStatusMessage(
                _("Could not find a valid email address"), type="error"
            )
            return

        sender_id = "{} ({}), {}".format(
            sender.getProperty("fullname"), sender.getId(), send_from_address
        )

        mail_host = getUtility(IMailHost)
        registry = getUtility(IRegistry)
        email_charset = registry.get("plone.email_charset", "utf-8")

        try:
            message = self.feedback_template(
                self,
                send_from_address=send_from_address,
                sender_id=sender_id,
                url=referer,
                subject=subject,
                message=message,
                encoding=email_charset,
                email_from_name=mail_settings.email_from_name,
            )

            message = message.encode(email_charset)

            mail_host.send(
                message,
                send_to_address,
                envelope_from,
                subject=subject,
                charset=email_charset,
            )
        except ConflictError:
            raise
        except Exception as e:
            logger.info("Unable to send mail: " + str(e))

            IStatusMessage(self.request).addStatusMessage(
                _("Unable to send mail."), type="error"
            )

            return

        IStatusMessage(self.request).addStatusMessage(_("Mail sent."), type="info")
        self.request.response.redirect(
            "{}/author/{}".format(self.portal.absolute_url(), author or "")
        )
        return


@implementer(IPublishTraverse)
class AuthorView(BrowserView):
    def __init__(self, context, request):
        super().__init__(context, request)

        self.username = None

    def publishTraverse(self, request, name):
        request["TraversalRequestNameStack"] = []

        self.username = name
        return self

    @property
    def is_anonymous(self):
        return self.portal_state.anonymous()

    @property
    def is_owner(self):
        current_member = self.portal_state.member()
        return current_member.getId() == self.username

    @property
    def author(self):
        username = self.username

        if not username:
            return {}

        authorinfo = self.membership_tool.getMemberInfo(username)
        portrait = self.membership_tool.getPersonalPortrait(username)

        if not authorinfo or not portrait:
            return {}

        return {"info": authorinfo, "portrait": portrait}

    @property
    def member_info(self):
        current_member = self.portal_state.member()
        if not current_member or not current_member.getId():
            return {"url": None, "email": None}

        return {
            "url": quote_plus(current_member.getId()),
            "email": current_member.getProperty("email"),
        }

    @property
    def author_content(self):
        results = []

        plone_view = self.context.restrictedTraverse("@@plone")

        brains = self.portal_catalog.searchResults(
            Creator=self.username, sort_on="created", sort_order="reverse"
        )

        for brain in brains[:10]:
            results.append(
                {
                    "title": pretty_title_or_id(self, brain),
                    "date": plone_view.toLocalizedTime(brain.Date),
                    "url": brain.getURL(),
                }
            )

        return results

    def home_folder(self, username):
        return self.membership_tool.getHomeFolder(id=username)

    def __call__(self):
        self.portal_properties = getUtility(IPropertiesTool)

        self.portal_catalog = getToolByName(self.context, "portal_catalog")

        # XXX: getUtility call does not work.
        self.membership_tool = getToolByName(self.context, "portal_membership")

        self.portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )

        self.feedback_form = AuthorFeedbackForm(self.context, self.request)
        self.feedback_form.update()
        self.feedback_form.widgets["author"].mode = HIDDEN_MODE
        self.feedback_form.widgets["referer"].mode = HIDDEN_MODE
        self.feedback_form.widgets["author"].value = self.username
        self.feedback_form.widgets["referer"].value = self.request.get(
            "referer", self.request.get("HTTP_REFERER", "unknown url")
        )

        registry = getUtility(IRegistry)
        security_settings = registry.forInterface(ISecuritySchema, prefix="plone")
        allow_anonymous_view_about = security_settings.allow_anon_views_about

        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        self.email_from_address = mail_settings.email_from_address

        if self.is_anonymous and not allow_anonymous_view_about:
            raise Unauthorized()

        return self.index()
