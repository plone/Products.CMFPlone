define([
  'expect',
  'sinon',
  'jquery',
  'pat-registry',
  'mockup-patterns-thememapper',
], function(expect, sinon, $, registry, RuleBuilderView ) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: Thememapper
  ========================== */

  describe('Thememapper', function () {

    beforeEach(function() {
      this.$el = $('' +
        '<div>' +
        '  <div class="pat-thememapper"' +
        ' data-pat-thememapper=\'filemanagerConfig:{"actionUrl":"/filemanager-actions"}; ' +
        ' themeUrl: "/theme_url";\'>'  +
        '  </div>' +
        '</div>').appendTo('body');
    });
    afterEach(function() {
      this.$el.remove();
    });

    it('Setup components', function() {
      expect($('.pat-filemanager', this.$el).length > 0).to.be.equal(false);
      // initialize pattern
      registry.scan(this.$el);

      this.clock = sinon.useFakeTimers();
      this.clock.tick(1000);
      expect($('.pat-filemanager', this.$el).length > 0).to.be.equal(true);
      expect($('#btngroup-mapper', this.$el).length > 0).to.be.equal(true);
      expect($('#btn-showinspectors', this.$el).length > 0).to.be.equal(true);
      expect($('#btn-buildrule', this.$el).length > 0).to.be.equal(true);
      expect($('#btn-previewtheme', this.$el).length > 0).to.be.equal(true);
      expect($('#btn-fullscreenEditor', this.$el).length > 0).to.be.equal(true);
      expect($('#btn-helpbutton', this.$el).length > 0).to.be.equal(true);
      expect($('#inspectors', this.$el).length > 0).to.be.equal(true);
      expect($('.container', this.$el).length > 0).to.be.equal(true);

      //This one is added after clicking the "fullscreen" button
      expect($('.closeeditor', this.$el).length === 0).to.be.equal(true);
    });

    it('Test buttons', function() {
      registry.scan(this.$el);

      this.clock = sinon.useFakeTimers();
      this.clock.tick(1000);

      expect($('.closeeditor', this.$el).length === 0).to.be.equal(true);
      expect($('.container', this.$el).hasClass('fullscreen')).to.be.equal(false);
      $('#btn-fullscreenEditor', this.$el).click();
      expect($('.container', this.$el).hasClass('fullscreen')).to.be.equal(true);
      expect($('.closeeditor', this.$el).length > 0).to.be.equal(true);

      $('.closeeditor', this.$el).click();
      expect($('.container', this.$el).hasClass('fullscreen')).to.be.equal(false);
      expect($('.closeeditor', this.$el).length === 0).to.be.equal(true);

      expect($('#inspectors', this.$el).is(':visible')).to.be.equal(false);
      $('#btn-showinspectors', this.$el).click();
      expect($('#inspectors', this.$el).is(':visible')).to.be.equal(true);
      $('#btn-showinspectors', this.$el).click();
      expect($('#inspectors', this.$el).is(':visible')).to.be.equal(false);
    });
  });
});
