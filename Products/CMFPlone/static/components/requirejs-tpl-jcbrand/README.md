requirejs-tpl
=============

*This is a fork which adds the features mentioned under the 0.0.3 release in the Changelog below*

This is an AMD loader for [UnderscoreJS micro-templates](http://underscorejs.org/#template) which can be used as a drop-in replacement to [ZeeAgency/requirejs-tpl](http://github.com/ZeeAgency/requirejs-tpl)

## Overview

- Uses the ``_.template()`` engine maintained by the UnderscoreJS team.
- Uses the official ``text`` loader plugin maintained by the RequireJS team.
- You don't have to specify the template file extension (``.html is assumed``, but this is configurable).

Notes:

- Both libraries can be removed at build-time using ``r.js``.
- The extension ``.html`` is assumed, and this makes loading templates similar to loading JavaScript files with RequireJS (all extensions are assumed).

## Changelog

0.0.1 Initial version

0.0.2 Various updates:
- Add template path option to tpl.js (thanks drewrichards)
- Updated require.js to 2.1.8 , and r.js to 2.1.8
- Updated underscore.js to 1.5.2

0.0.3 (Unreleased)
- Add option to configure underscore's template settings (i.e. to customize template delimeters)

## Installation

Download UnderscoreJS and RequireJS-text:

- [UndescoreJS](http://underscorejs.org)
- [RequireJS-text](http://requirejs.org/docs/download.html#text)

Typically, you would place them in a ``scripts/libs`` folder then create a ``scripts/main.js`` file to alias them and to shim UndescoreJS:

```
require.config({
  paths: {
    underscore: 'libs/underscore',
    text: 'libs/text'
    tpl: 'libs/tpl'
  },
  shim: {
    'underscore': {
      exports: '_'
    }
  }
});
```
## Usage

Specify the plugin using ``tpl!`` followed by the template file:

```
require(['backbone', 'tpl!template'], function (Backbone, template) {
  return Backbone.View.extend({
    initialize: function(){
      this.render();
    },
    render: function(){
      this.$el.html(template({message: 'hello'}));
  });
});
```
## Customization

You can specify the template file extension in your main.js:

```
require.config({

  // some paths and shims

  tpl: {
    extension: '.tpl' // default = '.html'
  }
});
```

Underscore allows you to configure the style of templating (more specifically,
the syntax for how variables are interpolated, conditional statements and
comments).  Refer to the [templateSettings](http://underscorejs.org/#template) variable.

Similarly to setting the template file extension, you can set
templateSettings in your main.js:

```
require.config({

    // Use Mustache style syntax for variable interpolation

    templateSettings: {
        evaluate : /\{\[([\s\S]+?)\]\}/g,
        interpolate : /\{\{([\s\S]+?)\}\}/g
    }
});
```

## Optimization

This plugin is compatible with [r.js](http://requirejs.org/docs/optimization.html).

Optimization brings three benefits to a project:

- The templates are bundled within your code and not dynamically loaded which reduces the number of HTTP requests.
- The templates are pre-compiled before being bundled which reduces the work the client has to do.
- You can use the compiled, non-minimized version of the templates to step over the code in a debugger.

The most important build options are:

```stubModules: ['underscore', 'text', 'tpl']```

The list of modules to stub out in the optimized file, i.e. the code is replaced with ``define('module',{});`` by ``r.js``

```removeCombined: true```

Removes from the output folder the files combined into a build.

## Example

### Using an existing web server

Copy the ``example`` and ``example-build`` folders to your web server (``text`` is not compatible with the ``file://`` protocol and opening ``index.hml`` directly from your browser will not work).

### Using a test server

Alternatively, you can use Connect and NodeJS to spin a web server:

Install ``connect`` using ``npm`` and launch the server with NodeJS:

```
  $ npm install -g connect
  $ npm link connect
  $ node server.js
```

Go to [http://localhost:9000/example](http://localhost:9000/example). Your browser should load:

- index.html
- require.js
- main.js
- tpl.js
- underscore.js
- text.js
- message.html

Go to [http://localhost:9000/example-build](http://localhost:9000/example-build). Your browser should load:

- index.html
- require.js
- main.js







