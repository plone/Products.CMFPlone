# enable use of utf-8 txt in tales inserts, until all code is changed
# This will only work for utf-8 encoded sites, but at least it will leave
# time to change Archetypes and Plone
import warnings, textwrap

def _unicode_replace(structure):
    if isinstance(structure, str):
        try:
            text = structure.decode('ascii')
        except UnicodeDecodeError:
            try:
                text = structure.decode('utf')
                warnings.warn(textwrap.dedent('''\

                *** *** Insertion of non-unicode non-ascii text in TAL is deprecated and will be broken in Plone 3.5 !!!

                %s...
                ''' % (repr(structure), )), DeprecationWarning, 2)
            except UnicodeDecodeError:
                # XXX Maybe, raise an exception here instead of a warning?
                warnings.warn(textwrap.dedent('''\

                *** *** Insertion of non-unicode non-ascii text in TAL is deprecated and will be broken in Plone 3.5 !!!
                *** *** In addition, the workaround is only provided for utf-8 content 
                *** *** so you MUST use utf-8 encoding in your site for this to work.

                %s...
                ''' % (repr(structure), )), DeprecationWarning, 2)
                # XXX the next line is fool-proof and will substitute ??-s if the encoding was not
                # unicode
                text = structure.decode('utf', 'replace')
    else:
        text = unicode(structure)
    return text

# Deal with the case where Unicode and encoded strings occur on the same tag.
# The mandatory PatchStringIO in PlacelessTranslationService deals only with
# joining complete tags together
def _nulljoin(valuelist):
    try:
        return ''.join(valuelist)
    except UnicodeDecodeError:
        text = u''
        for value in valuelist:
            text += _unicode_replace(value)
        return text

# monkey patch
import zope.tal.talinterpreter
zope.tal.talinterpreter.unicode = _unicode_replace

zope.tal.talinterpreter._nulljoin_old = zope.tal.talinterpreter._nulljoin
zope.tal.talinterpreter._nulljoin = _nulljoin
