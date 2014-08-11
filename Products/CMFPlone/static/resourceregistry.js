/* globals less:true, domready:true */

(function() {
  'use strict';

  // https://github.com/QueueHammer/codecraftsman.js/blob/master/codecraftsman.js#L23
  var ScriptPath = function() {
    var scriptPath = '', pathParts;
    try {
      throw new Error();
    } catch (e) {
      var stackLines = e.stack.split('\n');
      var callerIndex = 0;
      for (var i in stackLines){
        if (!stackLines[i].match(/http[s]?:\/\//)) {
          continue;
        }
        callerIndex = Number(i) + 2;
        break;
      }
      pathParts = stackLines[callerIndex].match(/((http[s]?:\/\/.+\/)([^\/]+\.js)):/);
    }

    this.fullPath = function() {
      return pathParts[1];
    };

    this.path = function() {
      return pathParts[2];
    };

    this.file = function() {
      return pathParts[3];
    };

    this.fileNoExt = function() {
      var parts = this.file().split('.');
      parts.length = parts.length !== 1 ? parts.length - 1 : 1;
      return parts.join('.');
    };
  };

  window.getScriptPath = function () {
    return new ScriptPath();
  };

  require(['jquery'], function($){
    $(document).ready(function() {

    var basePath = window.getScriptPath().path();

      requirejs.config({
        paths: {
        'ace': '++resource++bower/ace-builds/src/ace',
      'ace-theme-monokai': '++resource++bower/ace-builds/src/theme-monokai',
      'ace-mode-text': '++resource++bower/ace-builds/src/mode-text',
      'mockup-patterns-texteditor': '++resource++mockup/texteditor/pattern'
        } });
      require(['++resource++mockup/resourceregistry/pattern.js']);

  });
});

}());