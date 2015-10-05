define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-tree'
], function(expect, $, registry, Tree) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  describe('Tree', function() {
    it('loads the tree with data', function() {
      var $el = $('<div class="pat-tree"/>').appendTo('body');
      var tree = new Tree($el, {
        autoOpen: true,
        data: [{
          label: 'node1',
          children: [{
            label: 'child1'
          },{
            label: 'child2'
          }]
        },{
          label: 'node2',
          children: [{ label: 'child3' }]
        }]
      });
      expect(tree.$el.find('ul').length).to.be.equal(3);
    });
    it('load string of json', function() {
      var $el = $('<div class="pat-tree"/>').appendTo('body');
      var tree = new Tree($el, {
        autoOpen: true,
        data: '[' +
          '{"label": "node1",' +
          '"children": [{' +
            '"label": "child1"' +
            '},{' +
            '"label": "child2"' +
            '}]' +
          '}]'
      });
      expect(tree.$el.find('ul').length).to.be.equal(2);
    });
  });

});
