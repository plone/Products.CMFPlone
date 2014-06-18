define([
  'jquery',
  'expect',
  'react',
  'mockup-docs-navigation'
], function($, expect, React, Navigation) {
  'use strict';

  window.mocha.setup('bdd');

  describe('DocsApp:Navigation', function () {

    beforeEach(function() {
      this.$root = $('<div/>');
    });

    afterEach(function() {
      React.unmountComponentAtNode(this.$root[0]);
      this.$root.remove();
    });

    it('is positioned on the left by default', function() {
      var navigation = new Navigation();
      React.renderComponent(navigation, this.$root[0]);
      expect($('.navbar-left', this.$root).size()).to.be(1);
      expect($('li', this.$root).size()).to.be(0);
    });

    it('display pages', function() {
      var navigation = new Navigation({
        pages: [
          {id: 'page1', title: 'Page1', description: 'page1 desc'},
          {id: 'page2', title: 'Page2', description: 'page2 desc'}
        ]
      });
      React.renderComponent(navigation, this.$root[0]);
      expect($('.navbar-left', this.$root).size()).to.be(1);
      expect($('li', this.$root).size()).to.be(2);
    });

    it('positioned on the right side', function() {
      var navigation = new Navigation({ position: 'right' });
      React.renderComponent(navigation, this.$root[0]);
      expect($('.navbar-left', this.$root).size()).to.be(0);
      expect($('.navbar-right', this.$root).size()).to.be(1);
      expect($('li', this.$root).size()).to.be(0);
    });

  });

});
