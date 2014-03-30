import logging
from smtplib import SMTPException
 
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

log = logging.getLogger(__name__)

class ContactInfoView(BrowserView):
    """ """
    
    def __init__(self, context, request):
        super(ContactInfoView, self).__init__(context, request)
        self.errors = {}

    def __call__(self):
        if self.request.form.get('form.submitted'):
            self.validate()
            if not self.errors:
                self.send_feedback()
                return self.request.response.redirect('@@send-feedback-confirm')
        return self.index()

    def validate(self):
        form = self.request.form
        sender_from_address = form.get('sender_from_address')
        subject = form.get('subject')
        message = form.get('message')
        reg_tool = getToolByName(self.context, 'portal_registration')
        if not (sender_from_address and sender_from_address.strip()):
            self.errors['sender_from_address'] = \
                    _(u'Please enter your email address.')
        elif not reg_tool.isValidEmail(sender_from_address):
            self.errors['sender_from_address'] = \
                    _(u'Please submit a valid email address.')            

        if not (subject and subject.strip()):
            self.errors['subject'] = \
                    _('subject_required', u'Please enter a subject.')
        if not (message and message.strip()):
            self.errors['message'] = \
                    _('message_required', u'Please enter a message.')
        if self.errors:
            messages = IStatusMessage(self.request)
            messages.add(_(u'Please correct the indicated errors.'), "error")

    def send_feedback(self):
        context = self.context
        request = self.request
        urltool = getToolByName(context, 'portal_url')
        portal = urltool.getPortalObject()
        url = urltool()

        ## make these arguments?
        subject = request.get('subject', '')
        message = request.get('message', '')
        sender_from_address = request.get('sender_from_address', '')
        sender_fullname = request.get('sender_fullname', '')
        send_to_address = portal.getProperty('email_from_address')
        from_address = portal.getProperty('email_from_address')

        host = getToolByName(context,'MailHost') 
        encoding = portal.getProperty('email_charset')

        variables = {'sender_from_address' : sender_from_address,
                    'sender_fullname'     : sender_fullname,
                    'url'                 : url,
                    'subject'             : subject,
                    'message'             : message
                    }

        pmessage = IStatusMessage(self.request)
        try:
            message = context.restrictedTraverse('@@site-feedback-template')(context, **variables)
            message = message.encode(encoding)
            result = host.send(message, send_to_address, from_address,
                            subject=subject, charset=encoding)
        except (SMTPException, RuntimeError) , e: 
            log.error(e)
            plone_utils = getToolByName(context, 'plone_utils')
            exception = plone_utils.exceptionString()
            message = _(u'Unable to send mail: ${exception}',
                        mapping={u'exception': exception})
            pmessage.add(message, 'error')
            return

        ## clear request variables so form is cleared as well
        request.set('message', None)
        request.set('subject', None)
        request.set('sender_from_address', None)
        request.set('sender_fullname', None)
        
        pmessage.add(_(u'Mail sent.'))
