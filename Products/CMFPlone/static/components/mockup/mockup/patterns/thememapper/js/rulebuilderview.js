define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-patterns-filemanager-url/js/basepopover',
  'text!mockup-patterns-thememapper-url/templates/rulebuilder.xml',
], function($, _, Backbone, PopoverView, RulebuilderTemplate ) {
  'use strict';
  var rulebuilderTemplate = _.template(RulebuilderTemplate);

  var RuleBuilderView = PopoverView.extend({
    className: 'popover rulebuilderView',
    title: _.template('<%= _t("Rule Builder") %>'),
    content: rulebuilderTemplate,
    render: function() {
      var self = this;
      PopoverView.prototype.render.call(this);
      return this;
    },
    toggle: function(button, e) {
      PopoverView.prototype.toggle.apply(this, [button, e]);
      var self = this;
      if (!this.opened) {
        return;
      }else {
        this.app.ruleBuilder.checkSelectors();
      }
    }

  });

  return RuleBuilderView;
});
