/* Tree pattern.
 *
 * Options:
 * data(jSON): load data structure directly into tree (undefined)
 * dataUrl(jSON): Load data from remote url (undefined)
 * autoOpen(boolean): auto open tree contents (false)
 * dragAndDrop(boolean): node drag and drop support (false)
 * selectable(boolean): if nodes can be selectable (true)
 * keyboardSupport(boolean): if keyboard naviation is allowed (true)
 *
 * Documentation: # JSON node data
 *
 *    {{ example-1 }}
 *
 *    # Remote data URL
 *
 *    {{ example-2 }}
 *
 *    # Drag and drop
 *
 *    {{ example-3 }}
 *
 * Example: example-1
 *    <div class="pat-tree"
 *         data-pat-tree='data:[
 *          { "label": "node1",
 *            "children": [
 *              { "label": "child1" },
 *              { "label": "child2" }
 *            ]
 *          },
 *          { "label": "node2",
 *            "children": [
 *              { "label": "child3" }
 *            ]
 *          }
 *        ];'> </div>
 *
 * Example: example-2
 *    <div class="pat-tree"
 *         data-pat-tree="dataUrl:/docs/dev/tests/json/fileTree.json;
 *                        autoOpen:true"></div>
 *
 * Example: example-3
 *    <div class="pat-tree"
 *         data-pat-tree="dataUrl:/docs/dev/tests/json/fileTree.json;
 *                        dragAndDrop: true;
 *                        autoOpen: true"></div>
 *
 */


define([
  'jquery',
  'underscore',
  'mockup-patterns-base',
  'mockup-utils',
  'jqtree'
], function($, _, Base, utils) {
  'use strict';

  var Tree = Base.extend({
    name: 'tree',
    trigger: '.pat-tree',
    defaults: {
      dragAndDrop: false,
      autoOpen: false,
      selectable: true,
      keyboardSupport: true,
      onLoad: null
    },
    init: function() {
      var self = this;
      /* convert all bool options */
      for (var optionKey in self.options) {
        var def = self.defaults[optionKey];
        if (def !== undefined && typeof(def) === 'boolean') {
          self.options[optionKey] = utils.bool(self.options[optionKey]);
        }
      }

      if (self.options.dragAndDrop && self.options.onCanMoveTo === undefined) {
        self.options.onCanMoveTo = function(moved, target, position) {
          /* if not using folder option, just allow, otherwise, only allow if folder */
          return target.folder === undefined || target.folder === true;
        };
      }

      if (self.options.data && typeof(self.options.data) === 'string') {
        self.options.data = $.parseJSON(self.options.data);
      }
      if (self.options.onLoad !== null){
        // delay generating tree...
        var options = $.extend({}, self.options);
        $.getJSON(options.dataUrl, function(data) {
          options.data = data;
          delete options.dataUrl;
          self.tree = self.$el.tree(options);
          self.options.onLoad(self);
        });
      } else {
        self.tree = self.$el.tree(self.options);
      }
    }
  });


  return Tree;

});
