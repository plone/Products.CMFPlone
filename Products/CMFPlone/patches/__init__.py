import zserverPatch             # Identify Plone in HTTP Headers - netcraft
                                # here we come!

import addplonesitebutton       # Add an explicit button to add a new Plone
                                # site to the ZMI for faster access

import addzmisecuritywarning    # Add a warning to the ZMI security tab
                                # that you shouldn't use it

import dateIndexPatch           # Avoid OverflowErrors in Date*Indexes

import interfacePatch           # Fixes for interfaces tests that need to
                                # be merged upstream at some point

import unicodeFallbackPatch     # Makes the TAL engine in Zope 2.10+ accept
                                # utf-8 encoded strings as well as Unicode
