define([
  'expect',
  'jquery',
  'mockup-router',
  'backbone'
], function(expect, $, Router, Backbone) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  Router.start();

  describe('Router', function () {

    beforeEach(function() {
      var self = this;
      Router._changeLocation = function(path, hash) {
        self.routerPath = path + '#' + hash;
      };
    });

    afterEach(function() {
      this.routerPath = undefined;
    });

    it('routes and calls back', function() {
      var foo = {
        set: false
      };

      var callback = function() {
        this.set = true;
      };

      Router.addRoute('test', 'foo', callback, foo, '');
      Router.navigate('test:foo', {trigger: true});

      expect(foo.set).to.equal(true);
    });

    it('redirects from added action', function() {
      var foo = {
        set: false
      };

      var callback = function() {
        this.set = true;
      };

      expect(this.routerPath).to.equal(undefined);
      Router.addRoute('test', 'foo', callback, foo, '/');
      Router.redirect();

      expect(this.routerPath).to.equal('#!/test:foo');

      Router.reset();
    });

    it('basic redirect', function() {

      Router.addRedirect('/', 'test:two');
      Router.redirect();

      expect(this.routerPath).to.equal('#!/test:two');

      Router.reset();
    });

  });

});
