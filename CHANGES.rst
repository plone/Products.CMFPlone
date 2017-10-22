.. This file should contain the changes for the last release only, which
   will be included on the package's page on pypi. All older entries are
   kept in HISTORY.txt

Changelog
=========

5.2a1 (unreleased)
------------------

Breaking changes:

- Some tools from CMFCore are now utilities
  [pbauer]

- Remove five.pt for Zope 4
  [jensens]

- Changes for Zope 4 compatibility in maintenance controlpanel.
  [thet]

- Render exceptions using an exception view instead of standard_error_message.
  [davisagli]

New Features:

- *add item here*

Bug Fixes:

- Fallback for missing date in DefaultDublinCoreImpl no longer relies on
  bobobase_modification_time.
  [pbauer]

- Display real version of Zope, not of the empty meta-package Zope2.
  [pbauer]

- Add zcml-condition plone-52 for conditional configuration.
  [pbauer]
