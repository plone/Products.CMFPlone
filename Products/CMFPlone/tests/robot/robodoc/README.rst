==============
ROBODOC README
==============

The ``robodoc`` folder contains Robot Framework tests moved from the Plone documentation project.
Because they are designed to be run as test suite level stories (sandbox is cleared only when changing a robot file),
they are not integrated with zope.testrunner (``./bin/test``), but are designed to be run with Robot Framework test runner (``pybot``).


Installing Robot Framework
==========================

Most tools needed to run the tests and generate the screenshots are available from within a standard Plone buildout.coredev environment.
The only extra piece of software needed is `webdriver` for your operating system and browser of choice, and that browser.

Minimal buildout to generate a good enough Robot Framework test runner would look like the following:

.. code:: ini

   [buildout]
   extends = https://dist.plone.org/release/5-latest/versions.cfg
   parts = robot

   [robot]
   recipe = zc.recipe.egg
   eggs =
       Plone
       Pillow
       robotframework-selenium2screenshots
       plone.app.robotframework [debug]


Running the tests
=================

There are two possible ways to run the tests.

The first option is to run them with a single command:

.. code:: bash

   $ bin/pybot -v BROWSER:phantomjs src/Products.CMFPlone/Products/CMFPlone/tests/robot/robodoc/collaboration-advanced_control.robot

This command will 1) start up a Plone site, 2) run the defined test suite and 3) shut down the Plone site. It will take some time.
``-v BROWSER:phantomjs`` is optional, and will define a Robot Framework variable named ``BROWSER`` with value ``phantomjs``, effectively running the test suite using headless PhantomJS browser.

You can run multiple test suites in the same directory,

.. code:: bash

   $ bin/pybot -v BROWSER:phantomjs src/Products.CMFPlone/Products/CMFPlone/tests/robot/robodoc

will run all tests and generate all screenshots.

The second option is to first start a robot server and only then, in parallel, to execute the desired test suite:

.. code:: bash

   $ APPLY_PROFILES=plone.app.contenttypes:plone-content bin/robot-server plone.app.robotframework.PLONE_ROBOT_TESTING

or

.. code:: bash

   $ CONFIGURE_PACKAGES=plone.app.iterate APPLY_PROFILES=plone.app.contenttypes:plone-content,plone.app.iterate:default bin/robot-server plone.app.robotframework.PLONE_ROBOT_TESTING

and

   $ bin/pybot -v ROBOT_SERVER:True -v BROWSER:phantomjs src/Products.CMFPlone/Products/CMFPlone/tests/robot/robodoc/screenshot-tall/collaboration-advanced_control.robot

This option will be faster for subsequent runs.

Environment variable ``APPLY_PROFILES`` can be set to a comma separated list of Generic Setup profiles and is used by the very special test fixture ``PLONE_ROBOT_TESTING`` to prepare a Plone site with those profiles installed. There's also an another special variable ``CONFIGURE_PACKAGES`` that can be set to a comma separated list of package names (e.g. to ``plone.app.iterate``) to configure more profiles to be available for ``APPLY_PROFILES``.

A special variable ``ROBOT_SERVER:True`` must be set for Robot Framework test runner to fix the test suite to be aware of being executed against long-running robot server.

Screenshots for documentation
=============================

The screenshots are meant for the Plone documentation.

As there are still browser bugs, it is good to visually inspect them before they are uploaded in the repository
https://github.com/plone/documentation-roboshots

In there, the tagged releases should contain known-good-sets of screenshots for a particular Plone version.
