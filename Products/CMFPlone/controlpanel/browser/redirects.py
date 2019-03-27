# -*- coding: utf-8 -*-
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.batching.browser import PloneBatchView
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.utils import safe_text
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from six import StringIO
from six.moves.urllib.parse import urlparse
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory

import csv


_ = MessageFactory('plone')


def absolutize_path(path, is_source=True):
    """Create path including the path of the portal root.

    The path must be absolute, so starting with a slash.
    Or it can be a full url.

    If is_source is true, this is an alternative url
    that will point to a target (unknown here).

    If is_source is true, path is the path of a target.
    An object must exist at this path, unless it is a full url.

    Return a 2-tuple: (absolute redirection path,
    an error message if something goes wrong and otherwise '').
    """

    portal = getSite()
    err = None
    is_external_url = False
    if not path:
        if is_source:
            err = _(u"You have to enter an alternative url.")
        else:
            err = _(u"You have to enter a target.")
    elif not path.startswith('/'):
        if is_source:
            err = _(u"Alternative url path must start with a slash.")
        else:
            # For targets, we accept external urls.
            # Do basic check.
            parsed = urlparse(path)
            if parsed.scheme in ('https', 'http') and parsed.netloc:
                is_external_url = True
            else:
                err = _(u"Target path must start with a slash.")
    elif '@@' in path:
        if is_source:
            err = _(u"Alternative url path must not be a view.")
        else:
            err = _(u"Target path must not be a view.")
    else:
        context_path = "/".join(portal.getPhysicalPath())
        path = "{0}{1}".format(context_path, path)
    if not err and not is_external_url:
        catalog = getToolByName(portal, 'portal_catalog')
        if is_source:
            # Check whether already exists in storage
            storage = getUtility(IRedirectionStorage)
            if storage.get(path):
                err = _(u"The provided alternative url already exists!")
            else:
                # Check whether obj exists at source path.
                # A redirect would be useless then.
                if portal.unrestrictedTraverse(path, None) is not None:
                    err = _(u"Cannot use a working path as alternative url.")
        else:
            # Check whether obj exists at target path
            result = catalog.searchResults(path={"query": path})
            if len(result) == 0:
                err = _(u"The provided target object does not exist.")

    return path, err


class RedirectsView(BrowserView):
    def redirects(self):
        storage = getUtility(IRedirectionStorage)
        portal = getSite()
        context_path = "/".join(self.context.getPhysicalPath())
        portal_path = "/".join(portal.getPhysicalPath())
        redirects = storage.redirects(context_path)
        for redirect in redirects:
            path = redirect[len(portal_path) :]
            yield {'redirect': redirect, 'path': path}

    def __call__(self):
        storage = getUtility(IRedirectionStorage)
        request = self.request
        form = request.form
        status = IStatusMessage(self.request)
        errors = {}

        if 'form.button.Add' in form:
            redirection = form.get('redirection')
            if redirection and redirection.startswith('/'):
                # Check navigation root
                pps = getMultiAdapter(
                    (self.context, self.request), name='plone_portal_state'
                )
                nav_url = pps.navigation_root_url()
                portal_url = pps.portal_url()
                if nav_url != portal_url:
                    # We are in a navigation root different from the portal root.
                    # Update the path accordingly, unless the user already did this.
                    extra = nav_url[len(portal_url) :]
                    if not redirection.startswith(extra):
                        redirection = '{0}{1}'.format(extra, redirection)

            redirection, err = absolutize_path(redirection, is_source=True)
            if err:
                errors['redirection'] = err
                status.addStatusMessage(err, type='error')
            else:
                del form['redirection']
                storage.add(
                    redirection, "/".join(self.context.getPhysicalPath())
                )
                status.addStatusMessage(
                    _(u"Alternative url added."), type='info'
                )
        elif 'form.button.Remove' in form:
            redirects = form.get('redirects', ())
            for redirect in redirects:
                storage.remove(redirect)
            if len(redirects) > 1:
                status.addStatusMessage(
                    _(u"Alternative urls removed."), type='info'
                )
            else:
                status.addStatusMessage(
                    _(u"Alternative url removed."), type='info'
                )

        return self.index(errors=errors)

    @memoize
    def view_url(self):
        return self.context.absolute_url() + '/@@manage-aliases'


class RedirectionSet(object):
    def __init__(self, query=''):
        self.storage = getUtility(IRedirectionStorage)

        portal = getSite()
        self.portal_path = '/'.join(portal.getPhysicalPath())
        self.portal_path_len = len(self.portal_path)

        # noinspection PyProtectedMember
        if query:
            # with query path /Plone/news:
            # min_k is /Plone/news and
            # max_k is /Plone/newt
            # Apparently that is the way to minize the keys we ask.
            min_k = u'{0:s}/{1:s}'.format(self.portal_path, query.strip('/'))
            max_k = min_k[:-1] + chr(ord(min_k[-1]) + 1)
            self.data = self.storage._paths.keys(min=min_k, max=max_k)
        else:
            self.data = self.storage._paths.keys()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        redirect = self.data[item]
        if redirect.startswith(self.portal_path):
            path = redirect[self.portal_path_len :]
        else:
            path = redirect
        redirect_to = self.storage.get(redirect)
        if redirect_to.startswith(self.portal_path):
            redirect_to = redirect_to[self.portal_path_len :]
        return {'redirect': redirect, 'path': path, 'redirect-to': redirect_to}


class RedirectsBatchView(PloneBatchView):
    def make_link(self, pagenumber=None, omit_params=None):
        if omit_params is None:
            omit_params = ['ajax_load']
        url = super(RedirectsBatchView, self).make_link(
            pagenumber, omit_params
        )
        return u'{0:s}#manage-existing-aliases'.format(url)


class RedirectsControlPanel(BrowserView):
    def batching(self):
        return RedirectsBatchView(self.context, self.request)(self.redirects())

    @memoize
    def redirects(self):
        """ Get existing redirects from the redirection storage.
            Return dict with the strings redirect, path and redirect-to.
            Strip the id of the instance from path and redirect-to if
            it is present. (Seems to be always true)
            If id of instance is not present in path the var 'path' and
            'redirect' are equal.
        """
        return Batch(
            RedirectionSet(self.request.form.get('q', '')),
            15,
            int(self.request.form.get('b_start', '0')),
            orphan=1,
        )

    def __call__(self):
        storage = getUtility(IRedirectionStorage)
        portal = getSite()
        request = self.request
        form = request.form
        status = IStatusMessage(self.request)
        # We make a difference between errors when uploading a csv,
        # and errors in form submit.
        self.csv_errors = []
        self.form_errors = {}

        if 'form.button.Remove' in form:
            redirects = form.get('redirects', ())
            for redirect in redirects:
                storage.remove(redirect)
            if len(redirects) == 0:
                err = _(u"No alternative urls selected for removal.")
                status.addStatusMessage(err, type='error')
                self.form_errors['remove_redirects'] = err
            elif len(redirects) > 1:
                status.addStatusMessage(
                    _(u"Alternative urls removed."), type='info'
                )
            else:
                status.addStatusMessage(
                    _(u"Alternative url removed."), type='info'
                )
        elif 'form.button.Add' in form:
            err = self.add(
                form['redirection'],
                form['target_path'],
                portal,
                storage,
                status,
            )
            if not err:
                # clear our the form
                del form['redirection']
                del form['target_path']
        elif 'form.button.Upload' in form:
            self.upload(form['file'], portal, storage, status)

        return self.index()

    def add(self, redirection, target, portal, storage, status):
        """Add the redirections from the form. If anything goes wrong, do nothing.

        Returns error message or nothing.
        """
        abs_redirection, err = absolutize_path(redirection, is_source=True)
        if err:
            self.form_errors['redirection'] = err
        abs_target, target_err = absolutize_path(target, is_source=False)
        if target_err:
            self.form_errors['target_path'] = target_err

        if err and target_err:
            err = "{0} {1}".format(err, target_err)
        elif target_err:
            err = target_err
        else:
            if abs_redirection == abs_target:
                err = _(
                    u"Alternative urls that point to themselves will cause"
                    u" an endless cycle of redirects."
                )
                # TODO: detect indirect recursion

        if err:
            status.addStatusMessage(_(err), type='error')
        else:
            storage.add(abs_redirection, abs_target)
            status.addStatusMessage(
                _(u"Alternative url from {0} to {1} added.").format(
                    abs_redirection, abs_target
                ),
                type='info',
            )
        return err

    def upload(self, file, portal, storage, status):
        """Add the redirections from the CSV file `file`. If anything goes wrong, do nothing."""

        # No file picked. Theres gotta be a better way to handle this.
        if not file.filename:
            err = _(u"Please pick a file to upload.")
            status.addStatusMessage(err, type='error')
            self.form_errors['file'] = err
            return
        # Turn all kinds of newlines into LF ones. The csv module doesn't do
        # its own newline sniffing and requires either \n or \r.
        contents = safe_text(file.read()).splitlines()
        file = StringIO('\n'.join(contents))

        # Use first two lines as a representative sample for guessing format,
        # in case one is a bunch of headers.
        dialect = csv.Sniffer().sniff(file.readline() + file.readline())
        file.seek(0)

        successes = []  # list of tuples: (abs_redirection, target)
        had_errors = False
        for i, fields in enumerate(csv.reader(file, dialect)):
            if len(fields) == 2:
                redirection, target = fields
                abs_redirection, err = absolutize_path(
                    redirection, is_source=True
                )
                abs_target, target_err = absolutize_path(
                    target, is_source=False
                )
                if err and target_err:
                    err = "%s %s" % (err, target_err)  # sloppy w.r.t. i18n
                elif target_err:
                    err = target_err
                else:
                    if abs_redirection == abs_target:
                        # TODO: detect indirect recursion
                        err = _(
                            u"Alternative urls that point to themselves will cause"
                            u"an endless cycle of redirects."
                        )
            else:
                err = _(u"Each line must have 2 columns.")

            if not err:
                if not had_errors:  # else don't bother
                    successes.append((abs_redirection, abs_target))
            else:
                had_errors = True
                self.csv_errors.append(
                    dict(
                        line_number=i + 1,
                        line=dialect.delimiter.join(fields),
                        message=err,
                    )
                )

        if not had_errors:
            for abs_redirection, abs_target in successes:
                storage.add(abs_redirection, abs_target)
            status.addStatusMessage(
                _(
                    u"${count} alternative urls added.",
                    mapping={'count': len(successes)},
                ),
                type='info',
            )

    @memoize
    def view_url(self):
        return self.context.absolute_url() + '/@@redirection-controlpanel'
