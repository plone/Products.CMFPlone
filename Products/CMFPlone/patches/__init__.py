import addzmiplonesite          # Add an explicit link to add a new Plone
                                # site to the ZMI for faster access

import addzmisecuritywarning    # Add a warning to the ZMI security tab
                                # that you shouldn't use it

import dateIndexPatch           # Avoid OverflowErrors in Date*Indexes

import unicodeFallbackPatch     # Makes the TAL engine in Zope 2.10+ accept
                                # utf-8 encoded strings as well as Unicode

import csrf                     # Protects most important methods from
csrf.applyPatches()             # CSRF attacks

import speed                    # Various caching patches to improve speed

import securemailhost           # SecureMailHost BBB, remove in Plone 5.0
securemailhost.applyPatches()

import iso8601                  # use `DateTime.ISO8601` for `DateTime.ISO`
iso8601.applyPatches()

import security					# misc security fixes

import sendmail
sendmail.applyPatches()

try:
    # kupu may not be installed
    import kupu
except ImportError:
    pass

import addMember