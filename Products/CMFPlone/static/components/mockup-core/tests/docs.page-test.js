define([
  'jquery',
  'expect',
  'react',
  'mockup-docs-page'
], function($, expect, React, Page) {
  'use strict';

  window.mocha.setup('bdd');

  describe('DocsApp:Page', function () {

    beforeEach(function() {
      this.$root = $('<div/>');
    });

    afterEach(function() {
      React.unmountComponentAtNode(this.$root[0]);
      this.$root.remove();
    });

    it('without autotoc', function() {
      var page = new Page({
        id: 'somepage',
        title: 'some title',
        description: 'some description',
        text: '<p>some text</p>',
        autotoc: false
      });
      React.renderComponent(page, this.$root[0]);
      expect($('.page-header h1', this.$root).html()).to.be('some title');
      expect($('.page-header p', this.$root).html()).to.be('some description');
      expect($('.page-content > div', this.$root).html().toLowerCase()).to.be('<p>some text</p>');
    });

    it('autotoc and markdown', function() {
      var page = new Page({
        id: 'somepage',
        title: 'some title',
        description: 'some description',
        text: '# something',
        autotoc: true
      });
      React.renderComponent(page, this.$root[0]);
      expect($('.page-content > div', this.$root).hasClass('row')).to.be(true);
      expect($('.mockup-autotoc li a', this.$root).first().html()).to.be('something');
      expect($('.page-content > div > div.col-md-9 > h1', this.$root).attr('id')).to.be('mockup-autotoc_0');
      expect($('.page-content > div > div.col-md-9 > h1', this.$root).html()).to.be('something');
    });

    it('patterns', function() {
      var page = new Page({
        id: 'somepage',
        title: 'some title',
        description: 'some description',
        autotoc: false,
        patterns: [
          { id: 'somepattern',
            title: 'some Pattern',
            description: 'some pattern description.'
          }
        ]
      });
      React.renderComponent(page, this.$root[0]);
      expect($('.mockup-pattern-tile', this.$root).size()).to.be(1);
    });

  });

});
