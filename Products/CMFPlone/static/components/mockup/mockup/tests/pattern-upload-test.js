define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-upload'
], function(expect, $, registry, Upload) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: Upload
  ========================== */

  describe('Upload', function () {

    describe('Div', function () {
      beforeEach(function() {
        this.$el = $('' +
          '<div>' +
          '  <div class="pat-upload"' +
          '    data-pat-upload="url: /upload">' +
          '  </div>' +
          '</div>');
      });
      afterEach(function() {
        this.$el.remove();
      });

      it('default attributes', function() {
        expect($('.pat-upload', this.$el).hasClass('upload')).to.be.equal(false);
        expect($('.upload-area', this.$el).length).to.equal(0);
        expect($('.dz-message', this.$el).length).to.equal(0);
        // initialize pattern
        registry.scan(this.$el);

        expect($('.pat-upload', this.$el).hasClass('upload')).to.be.equal(true);
        expect($('.upload-area', this.$el).length).to.equal(1);
        expect($('.upload-area', this.$el).hasClass('dz-clickable')).to.be.equal(true);
        expect($('.dz-message', this.$el).length).to.equal(1);
        expect($('.dz-message', this.$el).hasClass('dz-default')).to.be.equal(false);
        expect($('.dz-message p', this.$el).html()).to.equal('Drop files here...');
      });
      it('change className data option', function() {
        var attr = $('.pat-upload', this.$el).attr('data-pat-upload');
        $('.pat-upload', this.$el).attr('data-pat-upload', attr + '; className: drop-zone');
        registry.scan(this.$el);
        expect($('.pat-upload', this.$el).hasClass('drop-zone')).to.be.equal(true);
      });
      it('update clickable data option to false', function() {
        var attr = $('.pat-upload', this.$el).attr('data-pat-upload');
        $('.pat-upload', this.$el).attr('data-pat-upload', attr + '; clickable: false');
        registry.scan(this.$el);
        expect($('.pat-upload', this.$el).hasClass('dz-clickable')).to.be.equal(false);
      });
      it('update clickable data option to false', function() {
        var attr = $('.pat-upload', this.$el).attr('data-pat-upload');
        $('.pat-upload', this.$el).attr('data-pat-upload', attr + '; clickable: false');
        registry.scan(this.$el);
        expect($('.pat-upload', this.$el).hasClass('dz-clickable')).to.be.equal(false);
      });
      it('update wrap data option to true', function() {
        expect($('.pat-upload', this.$el).parent().hasClass('upload-wrapper')).to.be.equal(false);
        var attr = $('.pat-upload', this.$el).attr('data-pat-upload');
        $('.pat-upload', this.$el).attr('data-pat-upload', attr + '; wrap: true');
        registry.scan(this.$el);
        expect($('.pat-upload', this.$el).parent().hasClass('upload-wrapper')).to.be.equal(true);
      });
      it('update autoCleanResults data option to true', function() {
        var attr = $('.pat-upload', this.$el).attr('data-pat-upload');
        $('.pat-upload', this.$el).attr('data-pat-upload', attr + '; autoCleanResults: true');
        registry.scan(this.$el);
        //TODO
      });

    });

  });
});
