define([
  'expect',
  'sinon',
  'backbone',
  'mockup-docs'
], function(expect, sinon, Backbone, DocsApp) {
  'use strict';

  window.mocha.setup('bdd');

  describe('DocsApp', function () {

    // Default option: Trigger and replace history.
    var opts = {trigger: true, replace: true};

    beforeEach(function() {
      // Stub route methods.
      sinon.stub(DocsApp.prototype, 'openPage');

      // Create app with stubs and manual fakes.
      this.app = new DocsApp();

      // Start history to enable routes to fire.
      Backbone.history.stop();
      Backbone.history.start({silent: true});

      // Spy on all route events.
      this.appSpy = sinon.spy();
      this.app.on('route', this.appSpy);
    });

    afterEach(function() {
      Backbone.history.stop();
      DocsApp.prototype.openPage.restore();
    });

    it('routes to a page', function() {
      this.app.navigate('some-page', opts);
      expect(DocsApp.prototype.openPage.calledTwice).to.be(true);
      expect(DocsApp.prototype.openPage.calledWithExactly('some-page', null)).to.be(true);
      expect(this.appSpy.calledOnce).to.be(true);
      expect(this.appSpy.calledWith('openPage', ['some-page', null])).to.be(true);
    });

  });

});
