""" 
Unittests for a PloneSite.

$Id: test_Portal.py,v 1.1.2.1 2002/10/07 14:34:19 dreamcatcher Exp $
"""

import unittest
import Zope     # product initialization
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Acquisition import aq_base

class PloneSiteTests( SecurityRequestTest ):

    def setUp(self):
        SecurityRequestTest.setUp(self)
        self.root.manage_addProduct[ 'CMFPlone' ].manage_addSite( 'testsite' )

    def _makeContent( self, site, portal_type, id='document', **kw ):

        site.invokeFactory( type_name=portal_type, id=id )
        content = getattr( site, id )

        if getattr( aq_base( content ), 'editMetadata', None ) is not None:
            content.editMetadata( **kw )

        return content

    def test_new( self ):

        site = self.root.testsite
        # catalog should have one entry, for index_html or frontpage
        self.assertEqual( len( site.portal_catalog ), 1 )

    def test_MetadataCataloguing( self ):

        site = self.root.testsite
        catalog = site.portal_catalog
        site.portal_membership.memberareaCreationFlag = 0

        portal_types = [ x for x in site.portal_types.listContentTypes()
                           if x not in ( 'Discussion Item'
                                       , 'Folder'
                                       , 'Topic'
                                       ) ]

        # at this point catalog should have one entry, for index_html
        # or frontpage
        self.assertEqual( len( catalog ), 1 )

        for portal_type in portal_types:

            doc = self._makeContent( site
                                   , portal_type=portal_type
                                   , title='Foo' )
            self.assertEqual( len( catalog ), 2 )

            # keys()[0] is the Plone Site frontpage or index_html document
            rid = catalog._catalog.paths.keys()[1]
            self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

            doc.editMetadata( title='Bar' )
            self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

            site._delObject( doc.getId() )
            self.assertEqual( len( catalog ), 1 )

    def test_DocumentEditCataloguing( self ):

        site = self.root.testsite
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='Document'
                               , title='Foo' )

        # keys()[0] is the Plone Site frontpage or index_html document
        rid = catalog._catalog.paths.keys()[1]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( text_format='structured-text'
                , text='Some Text Goes Here\n\n   A paragraph\n   for you.'
                )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_ImageEditCataloguing( self ):

        site = self.root.testsite
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='Image'
                               , title='Foo' )

        # keys()[0] is the Plone Site frontpage or index_html document
        rid = catalog._catalog.paths.keys()[1]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( 'GIF89a' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_FileEditCataloguing( self ):

        site = self.root.testsite
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='File'
                               , title='Foo' )

        # keys()[0] is the Plone Site frontpage or index_html document
        rid = catalog._catalog.paths.keys()[1]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( '%PDF-1.2\r' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_LinkEditCataloguing( self ):

        site = self.root.testsite
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='Link'
                               , title='Foo' )

        # keys()[0] is the Plone Site frontpage or index_html document
        rid = catalog._catalog.paths.keys()[1]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( 'http://www.example.com' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )

    def test_NewsItemEditCataloguing( self ):

        site = self.root.testsite
        catalog = site.portal_catalog

        doc = self._makeContent( site
                               , portal_type='News Item'
                               , title='Foo' )

        # keys()[0] is the Plone Site frontpage or index_html document
        rid = catalog._catalog.paths.keys()[1]

        doc.setTitle( 'Bar' )   # doesn't reindex
        self.assertEqual( _getMetadata( catalog, rid ), 'Foo' )

        doc.edit( '<h1>Extra!</h1>' )
        self.assertEqual( _getMetadata( catalog, rid ), 'Bar' )


def _getMetadata( catalog, rid, field='Title' ):
    md = catalog.getMetadataForRID( rid )
    return md[ field ]

def test_suite():

    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( PloneSiteTests ) )
    return suite


if __name__ == '__main__':

    unittest.main( defaultTest = 'test_suite' )
