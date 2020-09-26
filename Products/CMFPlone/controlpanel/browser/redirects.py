from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from csv import writer
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.batching.browser import PloneBatchView
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.utils import safe_text
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from io import StringIO
from urllib.parse import urlparse
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory

import csv
import logging
import tempfile

try:
    # use this to stream csv data if we can
    from ZPublisher.Iterators import filestream_iterator
except ImportError:
    filestream_iterator = None


_ = MessageFactory('plone')
logger = logging.getLogger(__name__)


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
            err = _("You have to enter an alternative url.")
        else:
            err = _("You have to enter a target.")
    elif not path.startswith('/'):
        if is_source:
            err = _("Alternative url path must start with a slash.")
        else:
            # For targets, we accept external urls.
            # Do basic check.
            parsed = urlparse(path)
            if parsed.scheme in ('https', 'http') and parsed.netloc:
                is_external_url = True
            else:
                err = _("Target path must start with a slash.")
    elif '@@' in path:
        if is_source:
            err = _("Alternative url path must not be a view.")
        else:
            err = _("Target path must not be a view.")
    else:
        context_path = "/".join(portal.getPhysicalPath())
        path = f"{context_path}{path}"
    if not err and not is_external_url:
        catalog = getToolByName(portal, 'portal_catalog')
        if is_source:
            # Check whether already exists in storage
            storage = getUtility(IRedirectionStorage)
            if storage.get(path):
                err = _("The provided alternative url already exists!")
            else:
                # Check whether obj exists at source path.
                # A redirect would be useless then.
                if portal.unrestrictedTraverse(path, None) is not None:
                    err = _("Cannot use a working path as alternative url.")
        else:
            # Check whether obj exists at target path
            result = catalog.searchResults(path={"query": path})
            if len(result) == 0:
                err = _("The provided target object does not exist.")

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

    def edit_for_navigation_root(self, redirection):
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
                redirection = f'{extra}{redirection}'
        # Finally, return the (possibly edited) redirection
        return redirection

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
                redirection = self.edit_for_navigation_root(redirection)

            redirection, err = absolutize_path(redirection, is_source=True)
            if err:
                errors['redirection'] = err
                status.addStatusMessage(err, type='error')
            else:
                del form['redirection']
                storage.add(
                    redirection,
                    "/".join(self.context.getPhysicalPath()),
                    manual=True,
                )
                status.addStatusMessage(
                    _("Alternative url added."), type='info'
                )
        elif 'form.button.Remove' in form:
            redirects = form.get('redirects', ())
            for redirect in redirects:
                storage.remove(redirect)
            if len(redirects) > 1:
                status.addStatusMessage(
                    _("Alternative urls removed."), type='info'
                )
            else:
                status.addStatusMessage(
                    _("Alternative url removed."), type='info'
                )

        return self.index(errors=errors)

    @memoize
    def view_url(self):
        return self.context.absolute_url() + '/@@manage-aliases'


class RedirectionSet:
    def __init__(self, query='', created='', manual=''):
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
            min_k = '{:s}/{:s}'.format(self.portal_path, query.strip('/'))
            max_k = min_k[:-1] + chr(ord(min_k[-1]) + 1)
            self.data = self.storage._paths.keys(
                min=min_k, max=max_k, excludemax=True
            )
        else:
            self.data = self.storage._paths.keys()
        if manual:
            # either 'yes' or 'no', otherwise we ignore the filter
            if manual == 'yes':
                manual = True
            elif manual == 'no':
                manual = False
            else:
                manual = ''
        if created:
            try:
                created = DateTime(created)
            except DateTimeError:
                logger.warning(
                    'Failed to parse as DateTime: %s', created
                )
                created = ''
        if created or manual != '':
            chosen = []
            for redirect in self.data:
                info = self.storage.get_full(redirect)
                if manual != '':
                    if info[2] != manual:
                        continue
                if created and info[1]:
                    if info[1] >= created:
                        continue
                chosen.append(redirect)
            self.data = chosen

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        redirect = self.data[item]
        if redirect.startswith(self.portal_path):
            path = redirect[self.portal_path_len :]
        else:
            path = redirect
        # redirect_to = self.storage.get(redirect)
        info = self.storage.get_full(redirect)
        redirect_to = info[0]
        if redirect_to.startswith(self.portal_path):
            redirect_to = redirect_to[self.portal_path_len :]
        return {
            'redirect': redirect,
            'path': path,
            'redirect-to': redirect_to,
            'datetime': info[1],
            'manual': info[2],
        }


class RedirectsBatchView(PloneBatchView):
    def make_link(self, pagenumber=None, omit_params=None):
        if omit_params is None:
            omit_params = ['ajax_load']
        url = super().make_link(
            pagenumber, omit_params
        )
        return f'{url:s}#manage-existing-aliases'


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
            RedirectionSet(
                query=self.request.form.get('q', ''),
                created=self.request.form.get('datetime', ''),
                manual=self.request.form.get('manual', ''),
            ),
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

        if 'form.button.Remove' in form or 'form.button.MatchRemove' in form:
            if 'form.button.Remove' in form:
                redirects = form.get('redirects', ())
            else:
                query = self.request.form.get('q', '')
                created = self.request.form.get('datetime', '')
                manual = self.request.form.get('manual', '')
                if created or manual or (query and query != '/'):
                    rset = RedirectionSet(
                        query=query, created=created, manual=manual
                    )
                    redirects = list(rset.data)
                else:
                    redirects = []
            for redirect in redirects:
                storage.remove(redirect)
            if len(redirects) == 0:
                err = _("No alternative urls selected for removal.")
                status.addStatusMessage(err, type='error')
                self.form_errors['remove_redirects'] = err
            elif len(redirects) > 1:
                status.addStatusMessage(
                    _("Alternative urls removed."), type='info'
                )
            else:
                status.addStatusMessage(
                    _("Alternative url removed."), type='info'
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
        elif 'form.button.Download' in form:
            return self.download()

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
            err = f"{err} {target_err}"
        elif target_err:
            err = target_err
        else:
            if abs_redirection == abs_target:
                err = _(
                    "Alternative urls that point to themselves will cause"
                    " an endless cycle of redirects."
                )
                # TODO: detect indirect recursion

        if err:
            status.addStatusMessage(_(err), type='error')
        else:
            storage.add(abs_redirection, abs_target, manual=True)
            status.addStatusMessage(
                _("Alternative url from {0} to {1} added.").format(
                    abs_redirection, abs_target
                ),
                type='info',
            )
        return err

    def upload(self, file, portal, storage, status):
        """Add the redirections from the CSV file `file`. If anything goes wrong, do nothing."""

        # No file picked. Theres gotta be a better way to handle this.
        if not file.filename:
            err = _("Please pick a file to upload.")
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

        # key is old path, value is tuple(new path, datetime, manual)
        successes = {}
        had_errors = False
        for i, fields in enumerate(csv.reader(file, dialect)):
            if len(fields) >= 2:
                redirection = fields[0]
                target = fields[1]

                now = None
                manual = True
                if len(fields) >= 3:
                    dt = fields[2]
                    if dt:
                        try:
                            now = DateTime(dt)
                        except DateTimeError:
                            logger.warning(
                                'Failed to parse as DateTime: %s', dt
                            )
                            now = None
                if len(fields) >= 4:
                    manual = fields[3].lower()
                    # Compare first character with false, no, 0.
                    if manual and manual[0] in 'fn0':
                        manual = False
                    else:
                        manual = True
                abs_redirection, err = absolutize_path(
                    redirection, is_source=True
                )
                abs_target, target_err = absolutize_path(
                    target, is_source=False
                )
                if err and target_err:
                    if (
                        i == 0
                        and not redirection.startswith('/')
                        and not target.startswith('/')
                    ):
                        # First line is a header.  Ignore this.
                        continue
                    err = f"{err} {target_err}"  # sloppy w.r.t. i18n
                elif target_err:
                    err = target_err
                else:
                    if abs_redirection == abs_target:
                        # TODO: detect indirect recursion
                        err = _(
                            "Alternative urls that point to themselves will cause"
                            " an endless cycle of redirects."
                        )
            else:
                err = _("Each line must have 2 or more columns.")

            if not err:
                if not had_errors:  # else don't bother
                    successes[abs_redirection] = (abs_target, now, manual)
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
            storage.update(successes)
            status.addStatusMessage(
                _(
                    "${count} alternative urls added.",
                    mapping={'count': len(successes)},
                ),
                type='info',
            )
        else:
            self.csv_errors.insert(
                0,
                dict(
                    line_number=0,
                    line='',
                    message=_(
                        'msg_delimiter',
                        default="Delimiter detected: ${delimiter}",
                        mapping={'delimiter': dialect.delimiter},
                    ),
                ),
            )

    def download(self):
        """Download all redirects as CSV.

        We save to a temporary file and try to stream it as a blob:
        with one million redirects you easily get 30 MB, which is slow as non-blob.
        """
        portal = getSite()
        portal_path = "/".join(portal.getPhysicalPath())
        len_portal_path = len(portal_path)
        file_descriptor, file_path = tempfile.mkstemp(
            suffix='.csv', prefix='redirects_'
        )
        with open(file_path, 'w') as stream:
            csv_writer = writer(stream)
            csv_writer.writerow(('old path', 'new path', 'datetime', 'manual'))
            storage = getUtility(IRedirectionStorage)
            paths = storage._paths
            # Note that the old and new paths start with /plone-site-id.
            # We strip this, as it is superfluous, and we would get errors
            # when using this download as an upload.
            for old_path, new_info in paths.items():
                if old_path.startswith(portal_path):
                    old_path = old_path[len_portal_path:]
                row = [old_path]
                if not isinstance(new_info, tuple):
                    # Old data: only a single path, no date and manual boolean.
                    new_info = (new_info,)
                row.extend(new_info)
                new_path = row[1]
                if new_path.startswith(portal_path):
                    row[1] = new_path[len_portal_path:]
                csv_writer.writerow(row)
        with open(file_path) as stream:
            contents = stream.read()
            length = len(contents)

        response = self.request.response
        response.setHeader('Content-Type', 'text/csv')
        response.setHeader('Content-Length', length)
        response.setHeader(
            'Content-Disposition', 'attachment; filename=redirects.csv'
        )
        if filestream_iterator is None:
            return contents
        # TODO: this is not enough to really stream the file.
        # I think we would need to handle Request-Range, like in the old
        # plone.app.blob.download.handleRequestRange
        return filestream_iterator(file_path, 'rb')

    @memoize
    def view_url(self):
        return self.context.absolute_url() + '/@@redirection-controlpanel'
