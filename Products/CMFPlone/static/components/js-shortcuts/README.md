# js-shortcuts

Easily add combination key-press event listeners in JavaScript. Useful for adding keyboard shortcuts to web applications.

Here's the [original version](http://www.openjs.com/scripts/events/keyboard_shortcuts/). I'm putting this up on GitHub to make loading this overusing Bower a bit easier.

## Usage

Basic Version

    shortcut.add("Ctrl+B", function () {
      window.alert("Make it Bold!");
    });

AngularJS

    app.controller('yourCtrl', function(jsShortcuts) {
    
      jsShortcuts.add("Ctrl+B", function () {
        window.alert("Make it Bold!");
      });  
      
    });

More information available on the [original doc](http://www.openjs.com/scripts/events/keyboard_shortcuts/) page.

## Installation

### Bower
Install via bower:

    bower install js-shortcuts --save 

and require the script:

    <script src="bower_components/js-shortcuts/js-shortcuts.js"></script>

### Angular
Install via bower as above. Use the AngularJS version of the script.

    <script src="bower_components/js-shortcuts/js-shortcuts-angular.js"></script>

Add the module `js-shortcuts` as a dependency to your app

    var app = angular.module('yourAwesomeApp', ['js-shortcuts']);


## License
BSD License
