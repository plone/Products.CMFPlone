define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-ui-url/views/popover',
  'translate',
  'pat-registry'
], function($, _, Backbone, PopoverView, _t, registry) {
  'use strict';

  var PropertiesView = PopoverView.extend({
    events: {
      'click button.applyBtn': 'applyButtonClicked',
      'click button.closeBtn': 'toggle'
    },
    submitText: _t('Apply'),
    initialize: function(options) {
      var self = this;
      self.app = options.app;
      self.className = 'popover ' + options.id;
      self.title = options.form.title || options.title;
      self.submitText = options.form.submitText || _t('Apply');
      self.submitContext = options.form.submitContext || 'primary';
      self.data = {};

      self.options = options;
      self.setContent(options.form.template);

      PopoverView.prototype.initialize.apply(this, [options]);
    },
    setContent: function(content){
      var self = this;
      var html = '<form>' + content + '</form>';
      html += '<button class="btn btn-block btn-' + self.submitContext + ' applyBtn">' + self.submitText + ' </button>';
      if(self.options.form.closeText){
        html += '<button class="btn btn-block btn-default closeBtn">' + self.options.form.closeText + ' </button>';
      }
      this.content = _.template(html);
    },
    getTemplateOptions: function(){
      var self = this;
      var items = [];
      self.app.selectedCollection.each(function(item){
        items.push(item.toJSON());
      });
      return $.extend({}, true, self.options, {
        items: items,
        data: self.data
      });
    },
    applyButtonClicked: function() {
      var self = this;
      var data = {};
      _.each(self.$el.find('form').serializeArray(), function(param){
        data[param.name] = param.value;
      });

      self.app.buttonClickEvent(this.triggerView, data);
      self.hide();
    },
    afterRender: function(){
      var self = this;
      if(self.options.form.dataUrl){
        self.$('.popover-content').html(_t('Loading...'));
        self.app.loading.show();
        $.ajax({
          url: self.options.form.dataUrl,
          dataType: 'json',
          type: 'POST',
          cache: false,
          data: {
            selection: JSON.stringify(self.app.getSelectedUids()),
            transitions: true,
            render: 'yes'
          }
        }).done(function(result){
          self.data = result.data || result;
          self.renderContent();
          registry.scan(self.$el);
        }).fail(function(){
          /* we temporarily set original html to a value here so we can
             render the updated content and then put the original back */
          var originalContent = self.content;
          self.setContent('<p>' + _t('Error loading popover from server.') + '</p>', false);
          self.renderContent();
          self.content = originalContent;
        }).always(function(){
          self.app.loading.hide();
        });
      }else{
        registry.scan(self.$el);
      }
    },
    toggle: function(button, e) {
      PopoverView.prototype.toggle.apply(this, [button, e]);
      var self = this;
      if (!self.opened) {
        return;
      }else{
        this.$el.replaceWith(this.render().el);
      }
    }
  });

  return PropertiesView;
});