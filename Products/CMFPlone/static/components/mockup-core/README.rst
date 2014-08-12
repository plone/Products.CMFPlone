Mockup Core is a collection of script which are needed to start Mockup_ based
project.


.. contents::


Inside you will find
====================

- a **patterns registry** which is used to register and initialize patterns.

- a **base pattern** which you use as a starting point to create new patterns.

- a **documentation application** which helps you document your patterns.

- a **yo generator** to quickly start your project (this is currently being
  developed).


Install & Run Tests
===================

Install Node version 0.10 or greater

    `Install using package manager, e.g. apt or yum
    <https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager>`_

    `Install without using package manager
    <https://github.com/joyent/node/wiki/Installation>`_

Install PhantomJS

    `Download and install PhantomJS
    <http://phantomjs.org/download.html>`_

Maybe use your package manager::

    $ apt-get install phantomjs

Now git clone & build Mockup::

    $ git clone https://github.com/plone/mockup-core.git
    $ cd mockup-core
    $ make bootstrap

Run tests with PhantomJS::

    $ make test

Run tests with Chrome::

    $ make test-dev


Report Issues
=============

All issues about Mockup_ related projects are tracked at:

https://github.com/plone/mockup/issues


Status of builds
================

.. image:: https://travis-ci.org/plone/mockup-core.png
   :target: https://travis-ci.org/plone/mockup-core
   :alt: Travis CI

.. image:: https://coveralls.io/repos/plone/mockup-core/badge.png?branch=master
   :target: https://coveralls.io/r/plone/mockup-core?branch=master
   :alt: Coveralls

.. image:: https://saucelabs.com/buildstatus/plone-mockup-core
   :target: https://saucelabs.com/u/plone-mockup-core
   :alt: Selenium Test Status

.. raw:: html

   <a href="https://saucelabs.com/u/plone-mockup-core">
       <img src="https://saucelabs.com/browser-matrix/plone-mockup-core.svg" alt="Selenium Tests Matrix" />
   </a>


Changelog
=========

v1.2.9 - 2014-08-12
-------------------

* fix tests and better karm reporting
  [thet]

v1.2.8 - 2014-08-11
-------------------

* finish removing jscs
  [vangheem]

v1.2.7 - 2014-08-10
-------------------

* correctly generate js min and dev files with maps
  [vangheem]

v1.2.6 - 2014-08-10
-------------------

* fix tests to work with latest mockup
  [vangheem]

* do not use jscs anymore
  [vangheem]


v1.2.4 - 2014-04-19
-------------------

* tinymce icons/font packaging fixed
  [garbas]


v1.2.3 - 2014-03-31
-------------------

* update bower packages:
   - react: 0.8.0 -> 0.10.0


v1.2.2 - 2014-03-31
-------------------

* update Saucelabs browser definitions
  [garbas]

* update bower packages:
   - sinon: 1.8.2 -> 1.9.0


v1.2.1 - 2014-03-30
-------------------

* add selectivizr, a utility that emulates CSS3 pseudo-classes and attribute
  selectors in Internet Explorer 6-8
  [garbas]

* all files in tests/ and js/ folder are now included in karma test runner
  [garbas]

* update node packages:
    - coveralls: 2.8.0 -> 2.10.0
    - grunt: 0.4.3 -> 0.4.4
    - grunt-contrib-jshint: 0.8.0 -> 0.9.2
    - grunt-contrib-less: 0.10.0 -> 0.11.0
    - grunt-jscs-checker: 0.4.0 -> 0.4.1
    - grunt-karma: 0.8.0 -> 0.8.2
    - karma: 0.12.0 -> 0.12.1
    - karma-coverage: 0.2.0 -> 0.2.1
    - karma-mocha: 0.1.1 -> 0.1.3
    - karma-sauce-launcher: 0.2.0 -> 0.2.4
    - mocha: 1.17.1 -> 1.18.2


v1.2.0 - 2014-03-25
-------------------

* karma/lib/config.js now also found when using nix
  [garbas]

* run multiple travis jobs for 2 browsers at the time
  [garbas]

* fixed typo in js/docs/view.js
  [garbas]

* add watcher for less files
  [garbas]

* make sure the router can find the pattern div
  [davisagli]


v1.1.1 - 2014-03-12
-------------------

* jscs linter added
  [garbas]

* fix grunthelper script
  [garbas]


v1.1.0 - 2014-03-12
-------------------

* update to bootstrap 3.1.0
  [garbas]

* move grunt helper script to mockup-core (from mockup) repository
  [garbas]


v1.0.1 - 2014-02-05
-------------------

* if the pattern file uses windows line endings (CRLF) remove the CR so the
  still matches.
  [domruf]

* DocsApp fix for loading patterns. Now it loads pattern as 'text!' using url
  and pattern via requirejs name registered in requirejs paths.
  [garbas]


v1.0.0 - 2014-01-21
-------------------

* Initial release.
  [garbas]


.. _Mockup: https://github.com/plone/mockup
