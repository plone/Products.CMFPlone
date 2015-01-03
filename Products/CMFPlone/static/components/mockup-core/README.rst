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


License
=======

The MIT License (MIT). Copyrights hold the Plone Foundation.
See `LICENSE.rst <LICENSE.rst>`_ for details.


Credits
=======

Originally created by `Rok Garbas <http://garbas.si/>`_ using parts of `Patterns
library <http://patternslib.com/>`_. Now maintained by the `Plone Foundation
<http://plone.org/>`_.


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


.. _Mockup: https://github.com/plone/mockup
