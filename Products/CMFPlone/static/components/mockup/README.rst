Plone Mockup is an ongoing effort to modernize Plone's javascript story. Check out examples and documentation at http://plone.github.io/mockup/

The Goals of Mockup
-------------------

1. Standardize configuration of patterns implemented in js
   to use HTML data attributes, so they can be developed
   without running a backend server.
2. Use modern AMD approach to declaring dependencies on other js libs.
3. Full unit testing of js

Install & Run Tests
-------------------
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

    $ git clone https://github.com/plone/mockup.git
    $ cd mockup
    $ make bootstrap

Run tests with PhantomJS::

    $ make test

Run tests with Chrome::

    $ make test-dev

Generate widgets pot file for plone translations::

    $ make i18n-dump


License
=======

The BSD 3-Clause License. Copyrights hold the Plone Foundation.
See `LICENSE.rst <LICENSE.rst>`_ for details.


Credits
-------

Originally created by `Rok Garbas <http://garbas.si/>`_ using parts of `Patterns
library <http://patternslib.com/>`_. Now maintained by the `Plone Foundation
<http://plone.org/>`_.


Status of builds
----------------

.. image:: https://travis-ci.org/plone/mockup.png
   :target: https://travis-ci.org/plone/mockup
   :alt: Travis CI

.. image:: https://coveralls.io/repos/plone/mockup/badge.png?branch=master
   :target: https://coveralls.io/r/plone/mockup?branch=master
   :alt: Coveralls

.. image:: https://d2weczhvl823v0.cloudfront.net/plone/mockup/trend.png
   :target: https://bitdeli.com/free
   :alt: Bitdeli
