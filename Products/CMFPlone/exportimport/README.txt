This directory needs to be made into a package.. this is where
all of the import and export handlers for the various Plone-specific
components should live.  Every product that requires special
handlers for the GenericSetup installation infrastructure should
have an exportimport module or package where those handlers should
live.
