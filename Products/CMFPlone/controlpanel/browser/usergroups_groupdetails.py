from Acquisition import aq_inner
from email.utils import getaddresses
from plone.base import PloneMessageFactory as _
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.usergroups import (
    UsersGroupsControlPanelView,
)
from Products.statusmessages.interfaces import IStatusMessage

class GroupDetailsControlPanel(UsersGroupsControlPanelView):
    def extract_invalid_emails(self, emails):
        """Validate a list of email addresses.
        
        Supports:
        - Multiple email addresses separated by commas
        - Email addresses with display names
        - Single email address strings
        - Lists of email addresses (from newline-separated input)
        
        Args:
            emails: String of comma/newline-separated emails or list of email strings
            
        Returns:
            list: List of invalid email addresses found
        """
        if not emails:
            return []
            
        # Convert input to list of email addresses
        if isinstance(emails, str):
            # Check if it's newline-separated
            if '\n' in emails:
                email_list = [email.strip() for email in emails.split('\n') if email.strip()]
            else:
                # Parse comma-separated emails with potential display names
                email_list = [emails]
        else:
            email_list = emails

        invalid_emails = []
        plone_utils = getToolByName(self.context, "plone_utils")

        # Process each email or group of emails
        for email_entry in email_list:
            # Parse addresses including display names
            parsed_addresses = getaddresses([email_entry])
            
            for name, addr in parsed_addresses:
                if not addr or not plone_utils.validateSingleEmailAddress(addr):
                    # If there was a display name, include it in the error message
                    if name:
                        invalid_emails.append(f"{name} <{addr}>" if addr else name)
                    else:
                        invalid_emails.append(addr if addr else email_entry)

        return invalid_emails

    def get_group_property(self, prop_id):
        """Retrieve group property, prioritizing request data if it's a POST request."""
        if self.request.method == "POST":
            return self.request.form.get(prop_id, None)
        
        try:
            return self.group.getProperty(prop_id, None)
        except AttributeError:
            pass

    def __call__(self):
        context = aq_inner(self.context)

        self.gtool = getToolByName(context, "portal_groups")
        self.gdtool = getToolByName(context, "portal_groupdata")
        self.regtool = getToolByName(context, "portal_registration")
        self.groupname = getattr(self.request, "groupname", None)
        self.grouproles = self.request.set("grouproles", [])
        self.group = self.gtool.getGroupById(self.groupname)
        self.grouptitle = self.groupname
        if self.group is not None:
            self.grouptitle = self.group.getGroupTitleOrName()

        self.request.set("grouproles", self.group.getRoles() if self.group else [])

        submitted = self.request.form.get("form.submitted", False)
        if submitted:
            CheckAuthenticator(self.request)

            msg = _("No changes made.")

            title = self.request.form.get("title", None)
            description = self.request.form.get("description", None)
            addname = self.request.form.get("addname", None)
            
            # Get email field(s) from the form
            emails = self.request.form.get("email", "")
            
            # Validate emails before proceeding
            invalid_emails = self.extract_invalid_emails(emails)
            if invalid_emails:
                msg = _(
                    "Invalid email address(es): ${emails}. Please correct them before proceeding.",
                    mapping={"emails": ", ".join(invalid_emails)},
                )
                IStatusMessage(self.request).add(msg, "error")
                return self.index()

            if addname:
                if not self.regtool.isMemberIdAllowed(addname):
                    msg = _("The group name you entered is not valid.")
                    IStatusMessage(self.request).add(msg, "error")
                    return self.index()

                success = self.gtool.addGroup(
                    addname,
                    (),
                    (),
                    title=title,
                    description=description,
                    REQUEST=self.request,
                )
                if not success:
                    msg = _(
                        "Could not add group ${name}, perhaps a user or "
                        "group with this name already exists.",
                        mapping={"name": addname},
                    )
                    IStatusMessage(self.request).add(msg, "error")
                    return self.index()

                self.group = self.gtool.getGroupById(addname)
                msg = _("Group ${name} has been added.", mapping={"name": addname})

            elif self.groupname:
                self.gtool.editGroup(
                    self.groupname,
                    roles=None,
                    groups=None,
                    title=title,
                    description=description,
                    REQUEST=context.REQUEST,
                )
                self.group = self.gtool.getGroupById(self.groupname)
                msg = _("Changes saved.")

            else:
                msg = _("Group name required.")

            processed = {}
            for id, property in self.gdtool.propertyItems():
                value = self.request.get(id, None)
                # Additional validation for any email properties
                if id.lower().endswith('email') and value:
                    invalid_emails = self.extract_invalid_emails(value)
                    if invalid_emails:
                        msg = _(
                            "Invalid email address(es) in ${field}: ${emails}",
                            mapping={"field": id, "emails": ", ".join(invalid_emails)},
                        )
                        IStatusMessage(self.request).add(msg, "error")
                        return self.index()
                processed[id] = value

            if self.group:
                self.group.setGroupProperties(processed)

            IStatusMessage(self.request).add(msg, type=self.group and "info" or "error")
            if self.group and not self.groupname:
                target_url = "{}/{}".format(
                    self.context.absolute_url(), "@@usergroup-groupprefs"
                )
                self.request.response.redirect(target_url)
                return ""

        return self.index()