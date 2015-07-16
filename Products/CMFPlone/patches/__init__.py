import addzmiplonesite          # Add an explicit link to add a new Plone
                                # site to the ZMI for faster access

import addzmisecuritywarning    # Add a warning to the ZMI security tab
                                # that you shouldn't use it

import unicodeFallbackPatch     # Makes the TAL engine in Zope 2.10+ accept
                                # utf-8 encoded strings as well as Unicode

import speed                    # Various caching patches to improve speed

import iso8601                  # use `DateTime.ISO8601` for `DateTime.ISO`
iso8601.applyPatches()

import security					# misc security fixes

import sendmail
sendmail.applyPatches()

import templatecookcheck        # Make sure templates aren't re-read in
                                # production sites

import dateIndexPatch