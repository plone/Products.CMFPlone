define([
  'jquery',
  'expect',
  'react',
  'mockup-docs-view'
], function($, expect, React, View) {
  'use strict';

  window.mocha.setup('bdd');

  describe('DocsApp:View', function () {

    beforeEach(function() {
      this.$root = $('<div/>');
    });

    afterEach(function() {
      React.unmountComponentAtNode(this.$root[0]);
      this.$root.remove();
    });

    it('default layout', function() {
      var view = new View();
      React.renderComponent(view, this.$root[0]);
      expect($('header', this.$root).size()).to.be(1);
      expect($('#content', this.$root).size()).to.be(1);
      expect($('footer', this.$root).size()).to.be(1);
    });

    it('switch pages', function() {
      var view = new View({
        pages: [
          { id: 'page1',
            title: 'page1 title',
            description: 'page1 description'
          },
          { id: 'page2',
            title: 'page2 title',
            description: 'page2 description'
          }
        ]
      });
      React.renderComponent(view, this.$root[0]);
      expect($('.header .nav li', this.$root).size()).to.be(2);
      expect($('.header .nav li.active', this.$root).size()).to.be(0);
      expect($('.page-index', this.$root).size()).to.be(1);
      view.setState({page: 'page1'});
      expect($('.page-index', this.$root).size()).to.be(0);
      expect($('.page-page1', this.$root).size()).to.be(1);
    });

  });

});
