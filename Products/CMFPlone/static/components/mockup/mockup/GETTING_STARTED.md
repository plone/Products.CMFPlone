# Before We Begin

To build and hack on Mockup you will need recent versions of git, node, npm and make.

Right now development of this project is being done primarily on Linux and OS X,
so setting up the tooling on MS Windows might be an adventure for you to explore --
though, all of the tools used have equivalent versions for that platform,
so with a little effort, it should work!

# Clone and Bootstrap

    $ git clone https://github.com/plone/mockup.git
    $ cd mockup
    $ make bootstrap

Now you have the complete source code for all Patterns from Mockup.
From here on you generate bundles of common functionality and minify them.

You're ready to start working on testable,
modular and beautiful JavaScript!

To see it in action, you must compile everything once, with

    $ make docs

and then you open index.html with your browser!

# Get hacking!

## Mockup Project Structure

 * `build/` : Contains all combined, optimized, and minimized JavaScript code,
   as well as compiled CSS (Less) and media files

 * `docs/` : Documentation files built with `make docs`

 * `js/` : Contains all of the modularized JavaScript code

    * `js/config.js` : Contains the RequireJS configuration

    * `js/bundles` : This is where a bundle is defined --
      a bundle is a set of requirements,
      code that specify the features being packaged and bootstraps your page.

    * `js/patterns` : Contains all individual, encapsulated patterns
      e.g. widgets.js

 * `less/` : Contains all the [Less](http://lesscss.org/) code for all the patterns and bundles

 * `lib/` : Contains external libraries not necessarily found in the bower repositories

 * `tests/` : Contains all tests for patterns and bundles, including general setup and configuration code

 * `Gruntfile.js` : Defines the directives for compiling Less,
   and for combining/optimizing/minimizing JavaScript to the defined bundles

 * `index.html` : The main source of documentation for the mockup project

 * `Makefile` : Scripts to build bundles, bootstrap the environment etc.


## What's a Pattern? What Are Bundles? How do they relate?

`Patterns` are units of JavaScript,
defined by a RequireJS/AMD style module.
Patterns may require other patterns to operate,
and may also require third party libraries.
Think of a pattern as a module -- encapsulated and separate,
and providing a widget or tool to be used by other patterns or in html.

`Bundles` are defined in a similar way to *Patterns* --
they are encapsulated bits of JavaScript that define requirements for a bundle and have some extra code in them that's useful for integrating the required patterns into Plone products.

Have a look at the [HelloWorld](#learn) example to see how to create your own Pattern and then how to bundle, test, build and use it.

# Bundling

To build all bundles:

    make bundles

To build one bundle:

    make bundle-widgets

# Testing

You can run tests with:

    make test

This will start a process which runs the tests when you change any of the js files.

If you just want to run tests just once you can use:

    make test-once

For debugging, or testing in a chrome browser use the following and open [localhost:9876](localhost:9876)

    make test-dev

If you want to just run the tests for a particular pattern you can use:

    make test pattern=foobar

or:

    make test-once pattern=foobar

or:

    make test-dev pattern=foobar

These will run only the tests that end with foobar-test.js

You can pass the ``verbose=true`` and ``debug=true`` command line options to
increase log output.


# Creating docs

First, build the documentation with:

    make docs

Then, start the python test server like so:

    python -m SimpleHTTPServer

After that, access the served site in a webbrowser under the url:

    http://localhost:8000


# Including a local mockup-core checkout for developing

If you want to also hack on mockup-core together with mockup and not push the
changes from mockup-core to github, you can include it from a local checkout.
Just replace the mockup-core line in bower.json with:

    "mockup-core": "file:///PATH/TO/mockup-core/.git/#BRANCHNAME"

Please note, you have to commit the changes on mockup-core before running
``make bootstrap``.

Alternatively, on UNIX based systems, simply make a symlink from
bower_components/mockup-core/ to your local mockup-core checkout.


# Upgrade from pre-2.0 to 2.0 based Mockup patterns

Since version 2.0, Mockup uses the Patternslib scanner and it's registry. This
allows us to: Use Patternslib patterns with Mockup/Plone and use Mockup
patterns with Patternslib outside of Plone. The integration with Patternslib
require that some small changes be made to newly developed Mockup patterns:

1. Patterns should now use pat-registry as dependency instead of
   mockup-registry.

        define([
            'jquery'
            'mockup-patterns-base',
            'pat-registry'
        ], function($, Base, registry) {

2. Patterns' selectors are now explicitly specified via the trigger attribute.
   For example:

       var Modal = Base.extend({
         name: 'modal',
         trigger: '.pat-modal',

3. Because of change 2, patterns now fire events via the emit method, instead
   of the trigger method.
