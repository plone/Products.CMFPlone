## Script (Python) "listMetaTags"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=List Dublin Core for '<meta>' tags
##
from DateTime import DateTime

metadataList = (
    # dublic core accessor name, metadata name
    ('Description',      'description'),
    ('Subject',          'keywords'),
    ('Description',      'DC.description'),
    ('Subject',          'DC.subject'),
    ('Creator',          'DC.creator'),
    ('Contributors',     'DC.contributors'),
    ('Publisher',        'DC.publisher'),
    ('CreationDate',     'DC.date.created',),
    ('ModificationDate', 'DC.date.modified'),
    ('Type',             'DC.type'),
    ('Format',           'DC.format'),
    ('Language',         'DC.language'),
    ('Rights',           'DC.rights'),
)

returnList = []

for accessor, key in metadataList:
    method = getattr(context, accessor, None)
    if not callable(method):
        # ups
        continue

    # Catch AttributeErrors raised by some AT applications
    try:
        value = method()
    except AttributeError:
        value = None
    if not value:
        # no data
        continue
    if accessor == 'Publisher' and value == 'No publisher':
        # No publisher is hardcoded (XXX: still?)
        continue
    if same_type(value, ()) or same_type(value, []):
        # convert a list to a string
        value = ', '.join(value)
    returnList.append( (key, value) )

# Portions of following code was copy/pasted from the listMetaTags script from
# CMFDefault.  This script is licensed under the ZPL 2.0 as stated here:
# http://www.zope.org/Resources/ZPL
# Zope Public License (ZPL) Version 2.0
# This software is Copyright (c) Zope Corporation (tm) and Contributors. All rights reserved.
created = context.CreationDate()

try:
    effective = context.EffectiveDate()
except AttributeError:
    effective = None

if effective and effective != 'None':
    effective = DateTime(effective)
else:
    effective = None

try:
    expires = context.ExpirationDate()
except AttributeError:
    expires = None 

if expires and expires != 'None':
    expires = DateTime(expires)
else:
    expires = None

#   Filter out DWIMish artifacts on effective / expiration dates
eff_str = ( effective and effective.year() > 1000
                      and effective != created ) and effective.Date() or ''
exp_str = ( expires and expires.year() < 9000 ) and expires.Date() or ''

if exp_str or exp_str:
    returnList.append( ( 'DC.date.valid_range'
                    , '%s - %s' % ( eff_str, exp_str ) ) )

return returnList
