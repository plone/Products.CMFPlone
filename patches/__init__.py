import zserverPatch             # Identify Plone in HTTP Headers - netcraft
                                # here we come!

import dateIndexPatch           # Avoid OverflowErrors in Date*Indexes

import interfacePatch           # Fixes for interfaces tests that need to
                                # be merged upstream at some point

import unicodeFallbackPatch     # Makes the TAL engine in Zope 2.10+ accept
                                # utf-8 encoded strings as well as Unicode

import httpresponse             # Temporarily fix bug in Z2's HTTPResponse

import components               # Temporarily fix bug in GenericSetup's
                                # components.py
