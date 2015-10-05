define([
  'expect',
  'jquery',
  'sinon',
  'pat-registry',
  'mockup-patterns-contentloader'
], function(expect, $, sinon, registry, ContentLoader) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

   /* ==========================
   TEST: Livesearch 
  ========================== */

  describe('Livesearch', function() {
    beforeEach(function() {
      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;
      this.server.respondWith('GET', /something\.html/, [
        200,
        { 'Content-Type': 'text/html' },
        '<html> ' +
        '<head></head>' +
        '<body> ' +
        '<div id="content">' +
        '<h1>Content from AJAX</h1>' +
        '<p>Ah, it is a rock, though. Should beat everything.</p>' +
        '</body> ' +
        '</html>'
      ]);
      this.clock = sinon.useFakeTimers();

      this.$el = $('<a href="#" class="pat-contentloader">Loader</a>').appendTo($('body'));

    });

    afterEach(function() {
      $('body').empty();
      this.server.restore();
      this.clock.restore();
    });

    it('load local content', function() {
      $('<div class="content">foobar</div>').appendTo($('body'));
      var loader = new ContentLoader(this.$el, {
        content: '.content'
      });
      this.$el.trigger('click');
      expect($('.content').size()).to.equal(2);
    });

    it('load local content to target', function() {
      $('<div class="content">foobar</div>').appendTo($('body'));
      $('<div class="target">blah</div>').appendTo($('body'));
      var loader = new ContentLoader(this.$el, {
        content: '.content',
        target: '.target'
      });
      this.$el.trigger('click');
      expect($('.content').size()).to.equal(2);
      expect($('.target').size()).to.equal(0);
    });

    it('load remote content', function() {
      var loader = new ContentLoader(this.$el, {
        url: 'something.html'
      });
      this.$el.trigger('click');
      this.clock.tick(1000);
      expect($('#content').size()).to.equal(1);
    });

  });

});
