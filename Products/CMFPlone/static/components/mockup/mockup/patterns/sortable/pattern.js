/* Sortable pattern.
 *
 * Options:
 *    selector(string): Selector to use to draggable items in pattern ('li')
 *    dragClass(string): Class to apply to original item that is being dragged. ('item-dragging')
 *    cloneClass(string): Class to apply to cloned item that is dragged. ('dragging')
 *    drop(function): callback function for when item is dropped (null)
 *
 * Documentation:
 *    # Default
 *
 *    {{ example-1 }}
 *
 *    # Table
 *
 *    {{ example-2 }}
 *
 * Example: example-1
 *    <ul class="pat-sortable">
 *      <li>One</li>
 *      <li>Two</li>
 *      <li>Three</li>
 *    </ul>
 *
 * Example: example-2
 *    <table class="table table-stripped pat-sortable"
 *           data-pat-sortable="selector:tr;">
 *      <tbody>
 *        <tr>
 *          <td>One One</td>
 *          <td>One Two</td>
 *        </tr>
 *        <tr>
 *          <td>Two One</td>
 *          <td>Two Two</td>
 *        </tr>
 *        <tr>
 *          <td>Three One</td>
 *          <td>Three Two</td>
 *        </tr>
 *      </tbody>
 *    </table>
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'jquery.event.drag',
  'jquery.event.drop'
], function($, Base, drag, drop) {
  'use strict';

  var SortablePattern = Base.extend({
    name: 'sortable',
    trigger: '.pat-sortable',
    defaults: {
      selector: 'li',
      dragClass: 'item-dragging',
      cloneClass: 'dragging',
      createDragItem: function(pattern, $el){
        return $el.clone().
          addClass(pattern.options.cloneClass).
          css({opacity: 0.75, position: 'absolute'}).appendTo(document.body);
      },
      drop: null // function to handle drop event
    },
    init: function() {
      var self = this;
      var start = 0;

      self.$el.find(self.options.selector).drag('start', function(e, dd) {
        var dragged = this;
        var $el = $(this);
        $(dragged).addClass(self.options.dragClass);
        drop({
          tolerance: function(event, proxy, target) {
            if ($(target.elem).closest(self.$el).length === 0) {
              /* prevent dragging conflict over another drag area */
              return;
            }
            var test = event.pageY > (target.top + target.height / 2);
            $.data(target.elem, 'drop+reorder', test ? 'insertAfter' : 'insertBefore' );
            return this.contains(target, [event.pageX, event.pageY]);
          }
        });
        start = $el.index();
        return self.options.createDragItem(self, $el);
      })
      .drag(function(e, dd) {
        /*jshint eqeqeq:false */
        $( dd.proxy ).css({
          top: dd.offsetY,
          left: dd.offsetX
        });
        var drop = dd.drop[0],
            method = $.data(drop || {}, 'drop+reorder');
        /* XXX Cannot use triple equals here */
        if (method && drop && (drop != dd.current || method != dd.method)) {
          $(this)[method](drop);
          dd.current = drop;
          dd.method = method;
          dd.update();
        }
      })
      .drag('end', function(e, dd) {
        var $el = $(this);
        $el.removeClass(self.options.dragClass);
        $(dd.proxy).remove();
        if (self.options.drop) {
          self.options.drop($el, $el.index() - start);
        }
      })
      .drop('init', function(e, dd ) {
        /*jshint eqeqeq:false */
        /* XXX Cannot use triple equals here */
        return (this == dd.drag) ? false: true;
      });

    }
  });

  return SortablePattern;

});


