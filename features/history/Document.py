##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
__version__ = "$Revision: 1.5 $"[11:-2]

ADD_CONTENT_PERMISSION = 'Add portal content'

import Globals, StructuredText, string, utils
from StructuredText.HTMLWithImages import HTMLWithImages
from Globals import DTMLFile, InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.PortalContent import PortalContent
from DublinCore import DefaultDublinCoreImpl
from OFS import History

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.utils import _format_stx, keywordsplitter
from utils import parseHeadersBody, SimpleHTMLParser, bodyfinder, _dtmldir

factory_type_information = ( { 'id'             : 'Document'
                             , 'meta_type'      : 'Document'
                             , 'description'    : """\
Documents can contain text that can be formatted using 'Structured Text.'"""
                             , 'icon'           : 'document_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addDocument'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'name'          : 'View'
                                  , 'action'        : 'document_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'name'          : 'Edit'
                                  , 'action'        : 'document_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'name'          : 'History'
                                  , 'action'        : 'history_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }                                 		
                                )
                             }
                           ,
                           )

def addDocument(self, id, title='', description='', text_format='',
                text=''):
    """ Add a Document """
    o = Document(id, title, description, text_format, text)
    self._setObject(id,o)


class CMFHtmlWithImages(HTMLWithImages):
    """ Special subclass of HTMLWithImages, overriding document() """
    def document(self, doc, level, output):
        """\
        HTMLWithImages.document renders full HTML (head, title, body).  For
        CMF Purposes, we don't want that.  We just want those nice juicy
        body parts perfectly rendered.
        """
        for c in doc.getChildNodes():
           getattr(self, self.element_types[c.getNodeName()])(c, level, output)

CMFHtmlWithImages = CMFHtmlWithImages()

class Document(PortalContent, DefaultDublinCoreImpl, History.Historical):
    """ A Document - Handles both StructuredText and HTML """

    __implements__ = ( PortalContent.__implements__
                     , DefaultDublinCoreImpl.__implements__
                     )
    manage_options=PortalContent.manage_options+History.Historical.manage_options
    meta_type = 'Document'
    effective_date = expiration_date = None
    text_format = ''
    _isDiscussable = 1

    _stx_level = 1                      # Structured text level

    _last_safety_belt_editor = ''
    _last_safety_belt = ''
    _safety_belt = ''

    # Declarative security (replaces __ac_permissions__)
    security = ClassSecurityInfo()

    def __init__(self, id, title='', description='', text_format='', text=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.title = title
        self.description = description
        self.text = text
        self.text_format = text_format
        self.edit( text_format=text_format, text=text )

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'manage_edit')
    manage_edit = DTMLFile('zmi_editDocument', _dtmldir)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'manage_editDocument' )
    def manage_editDocument(self, text_format, text, file='', REQUEST=None):
        """ A ZMI (Zope Management Interface) level editing method """
        self._edit(text_format, text, file)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(
                self.absolute_url()
                + '/manage_edit'
                + '?manage_tabs_message=Document+updated'
                )

    def _edit(self, text_format, text, file='', safety_belt=''):
        """ Edit the Document - Parses headers and cooks the body"""
        self.text = text
        headers = {}
        if file and (type(file) is not type('')):
            contents=file.read()
            if contents:
                text = self.text = contents

        headers, body, cooked, format = self.handleText(text, text_format)

        if not safety_belt:
            safety_belt = headers.get('SafetyBelt', '')
        if not self._safety_belt_update(safety_belt=safety_belt):
            msg = ("Intervening changes from elsewhere detected."
                   " Please refetch the document and reapply your changes."
                   " (You may be able to recover your version using the"
                   " browser 'back' button, but will have to apply them"
                   " to a freshly fetched copy.)")
            raise 'EditingConflict', msg

        self.text_format = format
        self.cooked_text = cooked
        self.text = body

        headers['Format'] = self.Format()
        new_subject = keywordsplitter(headers)
        headers['Subject'] = new_subject or self.Subject()
        haveheader = headers.has_key
        for key, value in self.getMetadataHeaders():
            if key != 'Format' and not haveheader(key):
                headers[key] = value
        
        self.editMetadata(title=headers['Title'],
                          subject=headers['Subject'],
                          description=headers['Description'],
                          contributors=headers['Contributors'],
                          effective_date=headers['Effective_date'],
                          expiration_date=headers['Expiration_date'],
                          format=headers['Format'],
                          language=headers['Language'],
                          rights=headers['Rights'],
                          )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'edit' )
    edit = WorkflowAction(_edit)

    security.declarePrivate('guessFormat')
    def guessFormat(self, text):
        """ Simple stab at guessing the inner format of the text """
        if utils.html_headcheck(text): return 'html'
        else: return 'structured-text'
    
    security.declarePrivate('handleText')
    def handleText(self, text, format=None, stx_level=None):
        """ Handles the raw text, returning headers, body, cooked, format """
        headers = {}
        body = cooked = text
        level = stx_level or self._stx_level

        if not format:
            format = self.guessFormat(text)

        if format == 'html':
            parser = SimpleHTMLParser()
            parser.feed(text)
            headers.update(parser.metatags)
            if parser.title:
                headers['Title'] = parser.title
            bodyfound = bodyfinder(text)
            if bodyfound:
                cooked = body = bodyfound
        else:
            headers, body = parseHeadersBody(text, headers)
            cooked = _format_stx(text=body, level=level)
            self._stx_level = level

        return headers, body, cooked, format
            
    security.declarePublic( 'getMetadataHeaders' )
    def getMetadataHeaders(self):
        """Return RFC-822-style header spec."""
        hdrlist = DefaultDublinCoreImpl.getMetadataHeaders(self)
        hdrlist.append( ('SafetyBelt', self._safety_belt) )
        return hdrlist

    security.declarePublic( 'SafetyBelt' )
    def SafetyBelt(self):
        """Return the current safety belt setting.
        For web form hidden button."""
        return self._safety_belt

    def _safety_belt_update(self, safety_belt=''):
        """Check validity of safety belt and update tracking if valid.

        Return 0 if safety belt is invalid, 1 otherwise.

        Note that the policy is deliberately lax if no safety belt value is
        present - "you're on your own if you don't use your safety belt".

        When present, either the safety belt token:
         - ... is the same as the current one given out, or
         - ... is the same as the last one given out, and the person doing the
           edit is the same as the last editor."""

        this_belt = safety_belt
        this_user = getSecurityManager().getUser().getUserName()

        if (# we have a safety belt value:
            this_belt
            # and the current object has a safety belt (ie - not freshly made)
            and (self._safety_belt is not None)
            # and the safety belt doesn't match the current one:
            and (this_belt != self._safety_belt)
            # and safety belt and user don't match last safety belt and user:
            and not ((this_belt == self._last_safety_belt)
                     and (this_user == self._last_safety_belt_editor))):
            # Fail.
            return 0

        # We qualified - either:
        #  - the edit was submitted with safety belt stripped, or
        #  - the current safety belt was used, or
        #  - the last one was reused by the last person who did the last edit.
        # In any case, update the tracking.

        self._last_safety_belt_editor = this_user
        self._last_safety_belt = this_belt
        self._safety_belt = str(self._p_mtime)

        return 1

    ### Content accessor methods
    security.declareProtected(CMFCorePermissions.View, 'SearchableText')
    def SearchableText(self):
        """ Used by the catalog for basic full text indexing """
        return "%s %s %s" % (self.title, self.description, self.text)

    security.declareProtected(CMFCorePermissions.View, 'CookedBody')
    def CookedBody(self, stx_level=None, setlevel=0):
        """\
        The prepared basic rendering of an object.  For Documents, this
        means pre-rendered structured text, or what was between the
        <BODY> tags of HTML.

        If the format is html, and 'stx_level' is not passed in or is the
        same as the object's current settings, return the cached cooked
        text.  Otherwise, recook.  If we recook and 'setlevel' is true,
        then set the recooked text and stx_level on the object.
        """
        if (self.text_format == 'html'
            or (stx_level is None)
            or (stx_level == self._stx_level)):
            return self.cooked_text
        else:
            cooked = _format_stx(self.text, stx_level)
            if setlevel:
                self._stx_level = stx_level
                self.cooked_text = cooked
            return cooked

    security.declareProtected(CMFCorePermissions.View, 'EditableBody')
    def EditableBody(self):
        """\
        The editable body of text.  This is the raw structured text, or
        in the case of HTML, what was between the <BODY> tags.
        """
        return self.text

    security.declareProtected(CMFCorePermissions.View, 'Description')
    def Description(self):
        """ Dublin core description, also important for indexing """
        return self.description
    
    security.declareProtected(CMFCorePermissions.View, 'Format')
    def Format(self):
        """ Returns a content-type style format of the underlying source """
        if self.text_format == 'html':
            return 'text/html'
        else:
            return 'text/plain'
    

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                             'setFormat' )
    def setFormat(self, value):
        value = str(value)
        if value == 'text/html':
            self.text_format = 'html'
        else:
            self.text_format = 'structured-text'
    setFormat = WorkflowAction(setFormat)

    ## FTP handlers
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP (and presumably FTP?) PUT requests """
        self.dav__init(REQUEST, RESPONSE)
        body = REQUEST.get('BODY', '')
        guessedformat = REQUEST.get_header('Content-Type', 'text/plain')
        ishtml = (guessedformat == 'text/html') or utils.html_headcheck(body)

        if ishtml: self.setFormat('text/html')
        else: self.setFormat('text/plain')

        try:
            self.edit(text_format=self.text_format, text=body)
        except 'EditingConflict', msg:
            # XXX Can we get an error msg through?  Should we be raising an
            #     exception, to be handled in the FTP mechanism?  Inquiring
            #     minds...
            get_transaction().abort()
            RESPONSE.setStatus(450)
            return RESPONSE

        RESPONSE.setStatus(204)
        return RESPONSE

    _htmlsrc = (
        '<html>\n <head>\n'
        ' <title>%(title)s</title>\n'
        '%(metatags)s\n'
        ' </head>\n'
        ' <body>\n%(body)s\n </body>\n'
        '</html>\n'
        )

    security.declareProtected( CMFCorePermissions.View, 'manage_FTPget' )
    def manage_FTPget(self):
        "Get the document body for FTP download (also used for the WebDAV SRC)"
        join = string.join
        lower = string.lower
        hdrlist = self.getMetadataHeaders()
        if self.Format() == 'text/html':
            hdrtext = ''
            for name, content in hdrlist:
                if lower(name) == 'title':
                    continue
                else:
                    hdrtext = '%s\n <meta name="%s" content="%s" />' % (
                        hdrtext, name, content)

            bodytext = self._htmlsrc % {
                'title': self.Title(),
                'metatags': hdrtext,
                'body': self.text,
                }
        else:
            hdrtext = join(map(lambda x: '%s: %s' % (
                x[0], x[1]), hdrlist), '\n')
            bodytext = '%s\n\n%s' % ( hdrtext, self.text )

        return bodytext

    security.declarePublic('isDiscussable')
    def isDiscussable(self):
        """ returns ._isDiscussable property """
        return self._isDiscussable

    security.declarePublic('manage_toggleDiscussability')
    def manage_toggleDiscussability(self, status):
        """ toggle individual class's discussability """
        if status: 
            self._isDiscussable = 1
        else: 
            self._isDiscussable = 0
       
    def manage_customHistoryCopy(self, keys):
        """ wraps manage_HistoryCopy and returns the view of the Document """
        self.manage_historyCopy(keys)
        return self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1'])
     
    security.declareProtected( CMFCorePermissions.View, 'manage_historyCompare')
    def manage_historyCompare(self, rev1, rev2, REQUEST,
                              historyComparisonResults=''):
        historyComparisonResults=History.html_diff( rev1.CookedBody(), rev2.CookedBody() )
        self.REQUEST.set('historyComparisonResults', historyComparisonResults)
        return self.history_comparison(self.REQUEST)

    security.declareProtected( CMFCorePermissions.View, 'get_size' )
    def get_size( self ):
        """ Used for FTP and apparently the ZMI now too """
        return len(self.manage_FTPget())

InitializeClass(Document)
