define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-autotoc'
], function(expect, $, Registry, AutoTOC) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  /* ==========================
   TEST: AutoTOC
  ========================== */

  describe('AutoTOC', function () {
    beforeEach(function() {
      this.$el = $('' +
        '<div class="pat-autotoc">' +
        ' <div>' +
        '   <h1>Title 1</h1>' +
        '   <h1>Title 2</h1>' +
        '   <h2>Title 2.1</h2>' +
        '   <h2>Title 2.3</h2>' +
        '   <h2>Title 2.4</h2>' +
        '   <h1>Title 3</h1>' +
        '   <h2>Title 3.1</h2>' +
        '   <h3>Title 3.1.1</h3>' +
        '   <h4>Title 3.1.1.1</h4>' +
        '   <h1 style="margin-top: 500px;">Title 4</h1>' +
        ' </div>' +
        ' <div class="placeholder" style="height: 1000px;">' +
        '   <div id="first-elem"></div>' +
        ' </div>' +
        '</div>').appendTo('body');
    });
    afterEach(function() {
      this.$el.remove();
    });
    it('by default creates TOC from h1/h2/h3', function() {
      expect($('> nav', this.$el).size()).to.equal(0);
      Registry.scan(this.$el);
      expect($('> nav', this.$el).size()).to.equal(1);
      expect($('> nav > a', this.$el).size()).to.equal(9);
      expect($('> nav > a.autotoc-level-1', this.$el).size()).to.equal(4);
      expect($('> nav > a.autotoc-level-2', this.$el).size()).to.equal(4);
      expect($('> nav > a.autotoc-level-3', this.$el).size()).to.equal(1);
      expect($('> nav > a.autotoc-level-4', this.$el).size()).to.equal(0);
    });
    it('sets href and id', function() {
      Registry.scan(this.$el);
      expect($('> nav > a:first', this.$el).attr('id')).to.equal('autotoc-item-autotoc-0');
      expect($('> nav > a:first', this.$el).attr('href')).to.equal('#autotoc-item-autotoc-0');
    });
    it('can be used as jQuery plugin as well', function () {
      expect($('> nav', this.$el).size()).to.equal(0);
      this.$el.patternAutotoc();
      expect($('> nav', this.$el).size()).to.equal(1);
    });
    it('can have custom levels', function() {
      this.$el.attr('data-pat-autotoc', 'levels: h1');
      expect($('> nav', this.$el).size()).to.equal(0);
      Registry.scan(this.$el);
      expect($('> nav', this.$el).size()).to.equal(1);
      expect($('> nav > a.autotoc-level-1', this.$el).size()).to.equal(4);
      expect($('> nav > a.autotoc-level-2', this.$el).size()).to.equal(0);
    });
    it('can be appended anywhere', function() {
      this.$el.attr('data-pat-autotoc', 'levels: h1;appendTo:.placeholder');
      expect($('> nav', this.$el).size()).to.equal(0);
      expect($('div.placeholder > nav', this.$el).size()).to.equal(0);
      Registry.scan(this.$el);
      expect($('> nav', this.$el).size()).to.equal(0);
      expect($('div.placeholder > nav', this.$el).size()).to.equal(1);
      expect($('div.placeholder', this.$el).children().eq(0).attr('id')).to.equal('first-elem');
      expect($('div.placeholder', this.$el).children().eq(1).attr('class')).to.equal('autotoc-nav');
    });
    it('can be prepended anywhere', function() {
      this.$el.attr('data-pat-autotoc', 'levels: h1;prependTo:.placeholder');
      expect($('> nav', this.$el).size()).to.equal(0);
      expect($('div.placeholder > nav', this.$el).size()).to.equal(0);
      Registry.scan(this.$el);
      expect($('> nav', this.$el).size()).to.equal(0);
      expect($('div.placeholder > nav', this.$el).size()).to.equal(1);
      expect($('div.placeholder', this.$el).children().eq(0).attr('class')).to.equal('autotoc-nav');
      expect($('div.placeholder', this.$el).children().eq(1).attr('id')).to.equal('first-elem');
    });
    it('custom className', function() {
      this.$el.attr('data-pat-autotoc', 'className:SOMETHING');
      Registry.scan(this.$el);
      expect(this.$el.hasClass('SOMETHING')).to.equal(true);
    });
    // it('scrolls to content', function(done) {
    //   Registry.scan(this.$el);
    //   expect($(document).scrollTop()).to.equal(0);
    //   if (navigator.userAgent.search('PhantomJS') >= 0) {
    //     // TODO Make this test work in PhantomJS as well as Chrome
    //     //      See https://github.com/ariya/phantomjs/issues/10162
    //     done();
    //   }
    //   $('> nav > a.autotoc-level-1', this.$el).last()
    //     .on('clicked.autodoc.patterns', function() {
    //       var documentOffset = Math.round($(document).scrollTop());
    //       var headingOffset = Math.round($('#autotoc-item-autotoc-8', this.$el).offset().top);
    //       expect(documentOffset).to.equal(headingOffset);
    //       done();
    //     })
    //     .click();
    // });
  });

});
