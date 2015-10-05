/* Pattern router
 */


define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone) {
  'use strict';

  var regexEscape = function(s) {
    return s.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  };

  var Router = Backbone.Router.extend({
    actions: [],
    redirects: {},
    addRoute: function(patternName, id, callback, context, pathExp, expReplace) {
      if (_.findWhere(this.patterns, {patternName: patternName, id: id}) === undefined) {
        this.actions.push({patternName: patternName, id: id, callback: callback, context: context, pathExp: pathExp, expReplace: expReplace});
      }
      var regex = new RegExp('(' + regexEscape(patternName) + ':' + regexEscape(id) + ')');
      this.route(regex, 'handleRoute');
    },
    addRedirect: function(pathExp, destination) {
      this.redirects[pathExp] = destination;
    },
    handleRoute: function(pattern) {
      var parts = pattern.split(':');
      var patternName = parts[0];
      var id = parts[1];
      var action = _.findWhere(this.actions, {patternName: patternName, id: id});
      if (action) {
        action.callback.call(action.context);
      }
    },
    redirect: function() {
      var path = window.parent.location.pathname,
          newPath,
          regex,
          hash;

      _.some(this.actions, function(action) {
        if (action.pathExp) {
          regex = new RegExp(action.pathExp);
          if (path.match(regex)) {
            hash = '!/' + action.patternName + ':' + action.id;
            var replaceWith = '';
            if (action.expReplace) {
              replaceWith = action.expReplace;
            }
            newPath = path.replace(regex, replaceWith);
            return true;
          }
        }
      }, this);

      if (hash === undefined) {
        for (var pathExp in this.redirects) {
          regex = new RegExp(pathExp);
          if (path.match(regex)) {
            hash = '!/' + this.redirects[pathExp];
            newPath = path.replace(regex, '');
            break;
          }
        }
      }

      if (hash !== undefined) {
        this._changeLocation.apply(this, [newPath, hash]);
      }
    },
    _changeLocation: function(path, hash) {
      window.parent.location.hash = hash;
      window.parent.location.pathname = path;
    },
    start: function() {
      Backbone.history.start();
    },
    reset: function() {
      this.actions = [];
    }

  });

  return new Router();

});
