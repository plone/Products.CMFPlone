
import imagePatch               # WAII and 508 we need more properties on image
                                # objects

import zserverPatch             # Identify Plone in HTTP Headers - netcraft
                                # here we come!

import setFormatPatch           # Patch DefaultDublinCoreImpl.setFormat to work
                                # around http://plone.org/collector/1323

import verifyObjectPastePatch   # Patch PortalFolder to work around
                                # http://plone.org/collector/2183
