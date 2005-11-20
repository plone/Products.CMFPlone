# script to convert all text of standard ATCT fields to utf-8

from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Products.CMFPlone import transaction

StringField = 'Products.Archetypes.Field.StringField'
TextField = 'Products.Archetypes.Field.TextField'

FieldsToConvert = [StringField, TextField]

def convert(self):

    if not hasattr(self, 'archetype_tool'):
        return 'Failure! Archetypes Tool not found.'

    proptool = self.portal_properties
    propsheet = getattr(proptool, 'site_properties', None)
    old_charset = propsheet.getProperty('default_charset')
    safeEditProperty(propsheet, 'default_charset', 'utf-8', 'string')

    print "------"
    print "Starting charset conversion"
    print "------"

    counter = [0]

    # call migrate on all at based objects
    attool = self.archetype_tool
    attool.enum(convertObj, old_charset, counter, self)

    print "------"
    print "Charset conversion finished."
    print "------"

    transaction.commit()

    return 'Success! %s objects converted.' % counter[0]

def convertObj(obj, old_charset, counter, portal):
    """ convert object"""
    if not obj.getCharset() == 'utf-8':
        fields = [f for f in obj.Schema().fields() if not f.isLanguageIndependent(obj)]
        for field in fields:
            name = field.getName()
            if field.getType() in FieldsToConvert and not name == 'allowDiscussion':
                text = field.getEditAccessor(obj)()
                try:
                    text = unicode(text, old_charset)
                    text = text.encode('utf-8')
                except UnicodeDecodeError:
                    print "Couldn't convert %s - field %s to utf-8" % (obj, name)

                mutator = field.getMutator(obj)
                result = mutator(text)

                if result is not None:
                    print 'Problem updating %s - field %s' % (obj, name)

    portal.portal_catalog.indexObject(obj)
    counter[0] += 1

