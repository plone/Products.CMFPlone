##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Dublin Core support for content types. """

from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from DateTime.DateTime import DateTime
from OFS.PropertyManager import PropertyManager
from zope.interface import implements

from Products.CMFCore.interfaces import ICatalogableDublinCore
from Products.CMFCore.interfaces import IDublinCore
from Products.CMFCore.interfaces import IMutableDublinCore
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.permissions import ModifyPortalContent
from Products.CMFPlone.permissions import View
from Products.CMFPlone.utils import WWW_DIR

_marker=[]

# For http://www.zope.org/Collectors/CMF/325
# We only really need this once, at startup.
_zone = DateTime().timezone()


def seq_strip(seq, stripper=lambda x: x.strip() ):
    """ Strip a sequence of strings.
    """
    if isinstance(seq, list):
        return map( stripper, seq )

    if isinstance(seq, tuple):
        return tuple( map( stripper, seq ) )

    raise ValueError, "%s of unsupported sequencetype %s" % ( seq, type( seq ) )


def tuplize( valueName, value, splitter=lambda x: x.split() ):

    if isinstance(value, tuple):
        return seq_strip( value )

    if isinstance(value, list):
        return seq_strip( tuple( value ) )

    if isinstance(value, basestring):
        return seq_strip( tuple( splitter( value ) ) )

    raise ValueError, "%s of unsupported type" % valueName


class DefaultDublinCoreImpl( PropertyManager ):

    """ Mix-in class which provides Dublin Core methods.
    """

    implements(IDublinCore, ICatalogableDublinCore, IMutableDublinCore)

    security = ClassSecurityInfo()

    def __init__( self
                , title=''
                , subject=()
                , description=''
                , contributors=()
                , effective_date=None
                , expiration_date=None
                , format='text/html'
                , language=''
                , rights=''
                ):
        now = DateTime()
        self.creation_date = now
        self.modification_date = now
        self.creators = ()
        self._editMetadata( title
                          , subject
                          , description
                          , contributors
                          , effective_date
                          , expiration_date
                          , format
                          , language
                          , rights
                          )

    #
    #  Set-modification-date-related methods.
    #  In DefaultDublinCoreImpl for lack of a better place.
    #

    # Class variable default for an upgrade.
    modification_date = None

    security.declarePrivate('notifyModified')
    def notifyModified(self):
        """ Take appropriate action after the resource has been modified.

        Update creators and modification_date.
        """
        self.addCreator()
        self.setModificationDate()

    security.declareProtected(ModifyPortalContent, 'addCreator')
    def addCreator(self, creator=None):
        """ Add creator to Dublin Core creators.
        """
        if creator is None:
            user = getSecurityManager().getUser()
            creator = user and user.getId()

        # call self.listCreators() to make sure self.creators exists
        if creator and not creator in self.listCreators():
            self.creators = self.creators + (creator, )

    security.declareProtected(ModifyPortalContent, 'setModificationDate')
    def setModificationDate(self, modification_date=None):
        """ Set the date when the resource was last modified.

        When called without an argument, sets the date to now.
        """
        if modification_date is None:
            self.modification_date = DateTime()
        else:
            self.modification_date = self._datify(modification_date)

    #
    #  DublinCore interface query methods
    #
    security.declareProtected(View, 'Title')
    def Title( self ):
        """ Dublin Core Title element - resource name.
        """
        return self.title

    security.declareProtected(View, 'listCreators')
    def listCreators(self):
        """ List Dublin Core Creator elements - resource authors.
        """
        if not hasattr(aq_base(self), 'creators'):
            # for content created with CMF versions before 1.5
            owner_tuple = self.getOwnerTuple()
            if owner_tuple:
                self.creators = (owner_tuple[1],)
            else:
                self.creators = ()
        return self.creators

    security.declareProtected(View, 'Creator')
    def Creator(self):
        """ Dublin Core Creator element - resource author.
        """
        creators = self.listCreators()
        return creators and creators[0] or ''

    security.declareProtected(View, 'Subject')
    def Subject( self ):
        """ Dublin Core Subject element - resource keywords.
        """
        return getattr( self, 'subject', () ) # compensate for *old* content

    security.declareProtected(View, 'Description')
    def Description( self ):
        """ Dublin Core Description element - resource summary.
        """
        return self.description

    security.declareProtected(View, 'Publisher')
    def Publisher( self ):
        """ Dublin Core Publisher element - resource publisher.
        """
        tool = getToolByName(self, 'portal_metadata', None)

        if tool is not None:
            return tool.getPublisher()

        return 'No publisher'

    security.declareProtected(View, 'listContributors')
    def listContributors(self):
        """ Dublin Core Contributor elements - resource collaborators.
        """
        return self.contributors

    security.declareProtected(View, 'Contributors')
    def Contributors(self):
        """ Deprecated alias of listContributors.
        """
        return self.listContributors()

    security.declareProtected(View, 'Date')
    def Date( self, zone=None ):
        """ Dublin Core Date element - default date.
        """
        if zone is None:
            zone = _zone
        # Return effective_date if set, modification date otherwise
        date = getattr(self, 'effective_date', None )
        if date is None:
            date = self.modified()
        return date.toZone(zone).ISO()

    security.declareProtected(View, 'CreationDate')
    def CreationDate( self, zone=None ):
        """ Dublin Core Date element - date resource created.
        """
        if zone is None:
            zone = _zone
        # return unknown if never set properly
        if self.creation_date:
            return self.creation_date.toZone(zone).ISO()
        else:
            return 'Unknown'

    security.declareProtected(View, 'EffectiveDate')
    def EffectiveDate( self, zone=None ):
        """ Dublin Core Date element - date resource becomes effective.
        """
        if zone is None:
            zone = _zone
        ed = getattr( self, 'effective_date', None )
        return ed and ed.toZone(zone).ISO() or 'None'

    security.declareProtected(View, 'ExpirationDate')
    def ExpirationDate( self, zone=None ):
        """ Dublin Core Date element - date resource expires.
        """
        if zone is None:
            zone = _zone
        ed = getattr( self, 'expiration_date', None )
        return ed and ed.toZone(zone).ISO() or 'None'

    security.declareProtected(View, 'ModificationDate')
    def ModificationDate( self, zone=None ):
        """ Dublin Core Date element - date resource last modified.
        """
        if zone is None:
            zone = _zone
        return self.modified().toZone(zone).ISO()

    security.declareProtected(View, 'Type')
    def Type( self ):
        """ Dublin Core Type element - resource type.
        """
        ti = self.getTypeInfo()
        return ti is not None and ti.Title() or 'Unknown'

    security.declareProtected(View, 'Format')
    def Format( self ):
        """ Dublin Core Format element - resource format.
        """
        return self.format

    security.declareProtected(View, 'Identifier')
    def Identifier( self ):
        """ Dublin Core Identifier element - resource ID.
        """
        # XXX: fixme using 'portal_metadata' (we need to prepend the
        #      right prefix to self.getPhysicalPath().
        return self.absolute_url()

    security.declareProtected(View, 'Language')
    def Language( self ):
        """ Dublin Core Language element - resource language.
        """
        return self.language

    security.declareProtected(View, 'Rights')
    def Rights( self ):
        """ Dublin Core Rights element - resource copyright.
        """
        return self.rights

    #
    #  DublinCore utility methods
    #
    def content_type( self ):
        """ WebDAV needs this to do the Right Thing (TM).
        """
        return self.Format()

    __FLOOR_DATE = DateTime( 1970, 0 ) # always effective

    security.declareProtected(View, 'isEffective')
    def isEffective( self, date ):
        """ Is the date within the resource's effective range?
        """
        pastEffective = ( self.effective_date is None
                       or self.effective_date <= date )
        beforeExpiration = ( self.expiration_date is None
                          or self.expiration_date >= date )
        return pastEffective and beforeExpiration

    #
    #  CatalogableDublinCore methods
    #
    security.declareProtected(View, 'created')
    def created( self ):
        """ Dublin Core Date element - date resource created.
        """
        # allow for non-existent creation_date, existed always
        date = getattr( self, 'creation_date', None )
        return date is None and self.__FLOOR_DATE or date

    security.declareProtected(View, 'effective')
    def effective( self ):
        """ Dublin Core Date element - date resource becomes effective.
        """
        marker = []
        date = getattr( self, 'effective_date', marker )
        if date is marker:
            date = getattr( self, 'creation_date', None )
        return date is None and self.__FLOOR_DATE or date

    __CEILING_DATE = DateTime( 2500, 0 ) # never expires

    security.declareProtected(View, 'expires')
    def expires( self ):
        """ Dublin Core Date element - date resource expires.
        """
        date = getattr( self, 'expiration_date', None )
        return date is None and self.__CEILING_DATE or date

    security.declareProtected(View, 'modified')
    def modified( self ):
        """ Dublin Core Date element - date resource last modified.
        """
        date = self.modification_date
        if date is None:
            # Upgrade.
            date = self.bobobase_modification_time()
            self.modification_date = date
        return date

    security.declareProtected(View, 'getMetadataHeaders')
    def getMetadataHeaders( self ):
        """ Return RFC-822-style headers.
        """
        hdrlist = []
        hdrlist.append( ( 'Title', self.Title() ) )
        hdrlist.append( ( 'Subject', ', '.join( self.Subject() ) ) )
        hdrlist.append( ( 'Publisher', self.Publisher() ) )
        hdrlist.append( ( 'Description', self.Description() ) )
        hdrlist.append( ( 'Contributors', '; '.join( self.Contributors() ) ) )
        hdrlist.append( ( 'Effective_date', self.EffectiveDate() ) )
        hdrlist.append( ( 'Expiration_date', self.ExpirationDate() ) )
        hdrlist.append( ( 'Type', self.Type() ) )
        hdrlist.append( ( 'Format', self.Format() ) )
        hdrlist.append( ( 'Language', self.Language() ) )
        hdrlist.append( ( 'Rights', self.Rights() ) )
        return hdrlist

    #
    #  MutableDublinCore methods
    #
    security.declarePrivate( '_datify' )
    def _datify( self, attrib ):
        if attrib == 'None':
            attrib = None
        elif not isinstance( attrib, DateTime ):
            if attrib is not None:
                attrib = DateTime( attrib )
        return attrib

    security.declareProtected(ModifyPortalContent, 'setTitle')
    def setTitle( self, title ):
        """ Set Dublin Core Title element - resource name.
        """
        self.title = title

    security.declareProtected(ModifyPortalContent, 'setCreators')
    def setCreators(self, creators):
        """ Set Dublin Core Creator elements - resource authors.
        """
        self.creators = tuplize('creators', creators)

    security.declareProtected(ModifyPortalContent, 'setSubject')
    def setSubject( self, subject ):
        """ Set Dublin Core Subject element - resource keywords.
        """
        self.subject = tuplize( 'subject', subject )

    security.declareProtected(ModifyPortalContent, 'setDescription')
    def setDescription( self, description ):
        """ Set Dublin Core Description element - resource summary.
        """
        self.description = description

    security.declareProtected(ModifyPortalContent, 'setContributors')
    def setContributors( self, contributors ):
        """ Set Dublin Core Contributor elements - resource collaborators.
        """
        semi_split = lambda s: map(lambda x: x.strip(), s.split( ';' ) )
        self.contributors = tuplize('contributors', contributors, semi_split)

    security.declareProtected(ModifyPortalContent, 'setEffectiveDate')
    def setEffectiveDate( self, effective_date ):
        """ Set Dublin Core Date element - date resource becomes effective.
        """
        self.effective_date = self._datify( effective_date )

    security.declareProtected(ModifyPortalContent, 'setExpirationDate')
    def setExpirationDate( self, expiration_date ):
        """ Set Dublin Core Date element - date resource expires.
        """
        self.expiration_date = self._datify( expiration_date )

    security.declareProtected(ModifyPortalContent, 'setFormat')
    def setFormat( self, format ):
        """ Set Dublin Core Format element - resource format.
        """
        self.format = format

    security.declareProtected(ModifyPortalContent, 'setLanguage')
    def setLanguage( self, language ):
        """ Set Dublin Core Language element - resource language.
        """
        self.language = language

    security.declareProtected(ModifyPortalContent, 'setRights')
    def setRights( self, rights ):
        """ Set Dublin Core Rights element - resource copyright.
        """
        self.rights = rights

    #
    #  Management tab methods
    #

    security.declarePrivate( '_editMetadata' )
    def _editMetadata( self
                     , title=_marker
                     , subject=_marker
                     , description=_marker
                     , contributors=_marker
                     , effective_date=_marker
                     , expiration_date=_marker
                     , format=_marker
                     , language=_marker
                     , rights=_marker
                     ):
        """ Update the editable metadata for this resource.
        """
        if title is not _marker:
            self.setTitle( title )
        if subject is not _marker:
            self.setSubject( subject )
        if description is not _marker:
            self.setDescription( description )
        if contributors is not _marker:
            self.setContributors( contributors )
        if effective_date is not _marker:
            self.setEffectiveDate( effective_date )
        if expiration_date is not _marker:
            self.setExpirationDate( expiration_date )
        if format is not _marker:
            self.setFormat( format )
        if language is not _marker:
            self.setLanguage( language )
        if rights is not _marker:
            self.setRights( rights )

    security.declareProtected(ModifyPortalContent, 'manage_metadata')
    manage_metadata = DTMLFile( 'zmi_metadata', WWW_DIR )

    security.declareProtected(ModifyPortalContent, 'manage_editMetadata')
    def manage_editMetadata( self
                           , title
                           , subject
                           , description
                           , contributors
                           , effective_date
                           , expiration_date
                           , format
                           , language
                           , rights
                           , REQUEST
                           ):
        """ Update metadata from the ZMI.
        """
        self._editMetadata( title, subject, description, contributors
                          , effective_date, expiration_date
                          , format, language, rights
                          )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                                + '/manage_metadata'
                                + '?manage_tabs_message=Metadata+updated.' )

    security.declareProtected(ModifyPortalContent, 'editMetadata')
    def editMetadata(self
                   , title=''
                   , subject=()
                   , description=''
                   , contributors=()
                   , effective_date=None
                   , expiration_date=None
                   , format='text/html'
                   , language='en-US'
                   , rights=''
                    ):
        """
        Need to add check for webDAV locked resource for TTW methods.
        """
        # as per bug #69, we cant assume they use the webdav
        # locking interface, and fail gracefully if they dont
        if hasattr(self, 'failIfLocked'):
            self.failIfLocked()

        self._editMetadata(title=title
                     , subject=subject
                     , description=description
                     , contributors=contributors
                     , effective_date=effective_date
                     , expiration_date=expiration_date
                     , format=format
                     , language=language
                     , rights=rights
                     )
        self.reindexObject()

InitializeClass(DefaultDublinCoreImpl)
