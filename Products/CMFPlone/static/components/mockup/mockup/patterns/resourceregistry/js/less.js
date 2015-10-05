define([
  'jquery',
  'mockup-ui-url/views/base',
  'underscore',
  'mockup-utils',
  'mockup-patterns-resourceregistry-url/js/fields',
], function($, BaseView, _, utils, fields) {
  'use strict';

  var LessVariablesView = BaseView.extend({
    tagName: 'div',
    className: 'tab-pane lessvariables',
    template: _.template(
      '<div class="buttons-container">' +
        '<div class="btn-group pull-right">' +
          '<button class="plone-btn plone-btn-default add-variable"><%- _t("Add variable") %></button>' +
          '<button class="plone-btn plone-btn-primary save"><%- _t("Save") %></button>' +
        '</div>' +
      '</div>' +
      '<div class="row clearfix">' +
        '<div class="form col-md-12"></div></div>'),
    events: {
      'click .plone-btn.save': 'saveClicked',
      'click .plone-btn.add-variable': 'addVariable'
    },

    initialize: function(options){
      BaseView.prototype.initialize.apply(this, [options]);
      this.loading = this.options.tabView.loading;
    },

    saveClicked: function(e){
      e.preventDefault();
      var self = this;
      self.options.tabView.saveData('save-less-variables', {
        data: JSON.stringify(self.options.data.lessvariables)
      });
    },

    addVariable: function(e){
      e.preventDefault();
      var self = this;
      self.options.data.lessvariables[utils.generateId('new-variable-')] = '';
      self.render();
    },

    inputChanged: function(){
      var self = this;
      var data = {};
      self.$('.form-group').each(function(){
        data[$(this).find('.field-name').val()] = $(this).find('.field-value').val();
      });
     self.options.data.lessvariables = data;
    },

    afterRender: function(){
      var self = this;
      var settings = self.options.data.lessvariables;
      var $form = self.$('.form');
      _.each(_.keys(settings), function(name){
        $form.append((new fields.VariableFieldView({
          registryData: settings,
          title: name,
          name: name,
          value: settings[name],
          onChange: function(){
            self.inputChanged();
          }
         }).render().el));
      });
    }
  });

  return LessVariablesView;

});
