define([
  'jquery',
  'mockup-ui-url/views/base',
  'underscore',
  'mockup-utils',
  'mockup-patterns-resourceregistry-url/js/fields',
], function($, BaseView, _, utils, fields) {
  'use strict';

  var PatternOptionsView = BaseView.extend({
    tagName: 'div',
    className: 'tab-pane patternoptions',
    template: _.template(
      '<div class="buttons-container">' +
        '<div class="btn-group pull-right">' +
          '<button class="plone-btn plone-btn-default add-pattern"><%- _t("Add pattern") %></button>' +
          '<button class="plone-btn plone-btn-primary save"><%- _t("Save") %></button>' +
        '</div>' +
      '</div>' +
      '<div class="row clearfix">' +
        '<div class="form col-md-12"></div></div>'),
    events: {
      'click .plone-btn.save': 'saveClicked',
      'click .plone-btn.add-pattern': 'addPattern'
    },

    initialize: function(options){
      BaseView.prototype.initialize.apply(this, [options]);
      this.loading = this.options.tabView.loading;
    },

    saveClicked: function(e){
      e.preventDefault();
      var self = this;
      self.options.tabView.saveData('save-pattern-options', {
        data: JSON.stringify(self.options.data.patternoptions),
      });
    },

    addPattern: function(e){
      e.preventDefault();
      var self = this;
      self.options.data.patternoptions[utils.generateId('new-pattern-')] = '';
      self.render();
    },

    inputChanged: function(){
      var self = this;
      var data = {};
      self.$('.form-group').each(function(){
        data[$(this).find('.field-name').val()] = $(this).find('.field-value').val();
      });
      self.options.data.patternoptions = data;
    },

    afterRender: function(){
      var self = this;
      var settings = self.options.data.patternoptions;
      var $form = self.$('.form');
      _.each(_.keys(settings), function(name){
        $form.append((new fields.PatternFieldView({
          registryData: settings,
          title: name,
          name: name,
          value: settings[name],
          onChange: function(e, field){
            try{
              // check that the json is in correct structure
              $.parseJSON(field.$el.find('.field-value').val());
              field.$el.removeClass('has-error').removeClass('has-feedback');
              field.$('.form-control-feedback').addClass('hidden');
            }catch(err){
              field.$el.addClass('has-error').addClass('has-feedback');
              field.$('.form-control-feedback').removeClass('hidden');
            }
            self.inputChanged();
          }
         }).render().el));
      });
    }
  });

  return PatternOptionsView;

});
