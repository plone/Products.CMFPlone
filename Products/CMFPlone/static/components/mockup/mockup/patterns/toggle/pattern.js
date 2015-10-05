/* Toggle pattern.
 *
 * Options:
 *    target(string): selector of the target elements to toggle ('undefied')
 *    targetScope(string): selector of a target scope element in anchestors ('global')
 *    attribute(string): element attribute which will be toggeled ('class')
 *    event(string): event which will trigger toggling ('click')
 *
 * Documentation:
 *    # Toggle itself
 *
 *    {{ example-1 }}
 *
 *    # Toggle all targets (global scope)
 *
 *    {{ example-2 }}
 *
 *    # Toggle specific target inside a target scope
 *
 *    {{ example-3 }}
 *
 *    # Toggle more than one target inside a specific target scope
 *
 *    {{ example-4 }}
 *
 *    # Toggle an element by hover event
 *
 *    {{ example-5 }}
 *
 *    # Toggle another element than class, like 'rel'
 *
 *    {{ example-6 }}
 *
 *    # Build a collapsable with toggle
 *
 *    {{ example-7 }}
 *
 * Example: example-1
 *    <button type="button"
 *            class="btn btn-default pat-toggle"
 *            data-pat-toggle="value:btn-lg;">This button goes bigger/smaller!</button>
 *
 * Example: example-2
 *    <div class="wrapper">
 *      <button type="button"
 *              class="btn btn-default pat-toggle"
 *              data-pat-toggle="value:label-success;target:.targetElement">This button is toggling the background of a element.</button><br />
 *      <p class="targetElement label label-default">Hello World</p>
 *    </div>
 *
 * Example: example-3
 *    <div class="wrapper">
 *      <div class="myScope">
 *        <button type="button"
 *                class="btn btn-default pat-toggle"
 *                data-pat-toggle="value:label-success;target:.targetElement;targetScope:.myScope;">toggle</button><br />
 *        <p class="targetElement label label-default">Hello World</p>
 *      </div>
 *      <div class="myScope">
 *        <button type="button"
 *                class="btn btn-default pat-toggle"
 *                data-pat-toggle="value:label-success;target:.targetElement;targetScope:.myScope;">toggle</button><br />
 *        <p class="targetElement label label-default">Hello World</p>
 *      </div>
 *    </div>
 *
 * Example: example-4
 *    <div class="wrapper">
 *      <div class="myScope">
 *        <button type="button"
 *                class="btn btn-default pat-toggle"
 *                data-pat-toggle="value:label-success;target:.targetElement;targetScope:.myScope;">toggle</button><br />
 *        <p class="targetElement label label-default">Hello World</p>
 *        <p class="targetElement label label-default">Hello again</p>
 *      </div>
 *      <div class="myScope">
 *        <button type="button"
 *                class="btn btn-default pat-toggle"
 *                data-pat-toggle="value:label-success;target:.targetElement;targetScope:.myScope;">toggle</button><br />
 *        <p class="targetElement label label-default">Hello World</p>
 *      </div>
 *    </div>
 *
 * Example: example-5
 *    <div class="wrapper">
 *      <div class="myScope">
 *        <button type="button"
 *                class="btn btn-default pat-toggle"
 *                data-pat-toggle="event:hover;value:label-success;target:.targetElement;targetScope:.myScope;">toggle</button><br />
 *        <p class="targetElement label label-default">Hello World</p>
 *      </div>
 *    </div>
 *
 * Example: example-6
 *    <div class="wrapper">
 *      <div class="myScope">
 *        <button type="button"
 *                class="btn btn-default pat-toggle"
 *                data-pat-toggle="attribute:rel; value:myRel; target:.targetElement; targetScope:.myScope">toggle</button><br />
 *        <p class="targetElement label label-default">Hello World</p>
 *      </div>
 *    </div>
 *
 * Example: example-7
 *    <div class="panel panel-default">
 *      <div class="panel-heading">
 *        <a class="btn btn-default pat-toggle"
 *           data-pat-toggle="value:in; target:.collapse; targetScope:.panel">toggle</a>
 *      </div>
 *      <div>
 *        <ul class="collapse in">
 *          <li>We use toggle for</li>
 *          <li>toggling collapsable CSS classes</li>
 *          <li>this is awesome</li>
 *        </ul>
 *      </div>
 *    </div>
 *
 */


define([
  'jquery',
  'mockup-patterns-base'
], function($, Base, undefined) {
  'use strict';

  var Toggle = Base.extend({
    name: 'toggle',
    trigger: '.pat-toggle',
    defaults: {
      attribute: 'class',
      event: 'click',
      targetScope: 'global'
    },
    init: function() {
      var self = this;

      if (!self.options.target) {
        self.$target = self.$el;
      } else if (self.options.targetScope === 'global') {
        self.$target = $(self.options.target);
      } else {
        //self.$target = self.$el[self.options.menu](self.options.target);
        self.$target = self.$el.parents(self.options.targetScope).first().find(self.options.target);
      }

      if (!self.$target || self.$target.size() === 0) {
        $.error('No target found for "' + self.options.target + '".');
      }

      self.on(self.options.event, function(e) {
        self.toggle();
        e.stopPropagation();
        e.preventDefault();
      });
    },
    isMarked: function() {
      var self = this;
      var marked = false;

      for (var i = 0; i < this.$target.length; i = i + 1) {
        if (self.options.attribute === 'class') {
          if (this.$target.eq(i).hasClass(this.options.value)) {
            marked = true;
          } else {
            marked = false;
            break;
          }
        } else {
          if (this.$target.eq(i).attr(this.options.attribute) === this.options.value) {
            marked = true;
          } else {
            marked = false;
            break;
          }
        }
      }
      return marked;
    },
    toggle: function() {
      var self = this;
      if (self.isMarked()) {
        self.remove();
      } else {
        self.add();
      }
    },
    remove: function() {
      var self = this;
      self.emit('remove-attr');
      if (self.options.attribute === 'class') {
        self.$target.removeClass(self.options.value);
      } else {
        self.$target.removeAttr(self.options.attribute);
      }
      self.emit('attr-removed');
    },
    add: function() {
      var self = this;
      self.emit('add-attr');
      if (self.options.attribute === 'class') {
        self.$target.addClass(self.options.value);
      } else {
        self.$target.attr(self.options.attribute, self.options.value);
      }
      self.emit('added-attr');
    }
  });

  return Toggle;

});
