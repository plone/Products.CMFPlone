define([
  'jquery',
  'underscore',
  'mockup-ui-url/views/base',
  'mockup-patterns-sortable',
  'mockup-patterns-select2',
  'translate'
], function($, _, BaseView, Sortable, Select2, _t) {
  'use strict';


  var ResourceDisplayFieldView = BaseView.extend({
    tagName: 'div',
    className: 'form-group',
    template: _.template(
      '<label class="col-sm-3 control-label"><%- title %></label>' +
      '<div class="col-sm-9">' +
        '<strong><%- value %></strong><br/>' +
        '<%= description %>' +
      '</div>'),
    initialize: function(options) {
      this.options = options;
      for (var key in this.options) {
        this[key] = this.options[key];
      }
      if (! this.value) {
        this.template = _.template('');
      }
    },
    serializedModel: function(){
    },
    afterRender: function(){
      this.$el.addClass('field-' + this.options.name);
    }

  });

  var ResourceInputFieldView = BaseView.extend({
    tagName: 'div',
    className: 'form-group',
    events: {
      'change input': 'inputChanged',
      'keyup input': 'textChanged'
    },
    template: _.template(
      '<label class="col-sm-3 control-label"><%- title %></label>' +
      '<div class="col-sm-9">' +
        '<input class="form-control input-sm" name="name" value="<%- value %>" />' +
        '<%= description %>' +
      '</div>'),
    timeout: -1,

    serializedModel: function(){
      return $.extend({}, {description: ''}, this.options);
    },

    textChanged: function(){
      var self = this;
      if(self.timeout){
        clearTimeout(self.timeout);
      }
      self.timeout = setTimeout(function(){
        self.inputChanged();
      }, 200);
    },

    inputChanged: function(){
      this.options.registryData[this.options.name] = this.$('input').val();
      $(document).trigger('resource-data-changed');
    },

    afterRender: function(){
      this.$el.addClass('field-' + this.options.name);
    }

  });

  var VariableFieldView = ResourceInputFieldView.extend({
    template: _.template(
      '<div class="col-sm-4">' +
        '<input class="form-control input-sm field-name" value="<%- name %>" />' +
      '</div>' +
      '<div class="col-sm-7">' +
        '<input class="form-control input-sm field-value" value="<%- value %>" />' +
      '</div>' +
      '<div class="col-sm-1">' +
        '<button class="plone-btn plone-btn-danger plone-btn-xs">Remove</button>' +
      '</div>'),
    events: {
      'change input': 'inputChanged',
      'keyup input': 'textChanged',
      'click .plone-btn-danger': 'removeClicked'
    },
    removeClicked: function(e){
      e.preventDefault();
      this.$el.remove();
      this.inputChanged();
    },
    inputChanged: function(e){
      if(this.options.onChange){
        this.options.onChange(e, this);
      }
    }
  });


  var PatternFieldView = VariableFieldView.extend({
    events: {
      'change input': 'inputChanged',
      'keyup input': 'textChanged',
      'change textarea': 'inputChanged',
      'keyup textarea': 'textChanged',
      'click .plone-btn-danger': 'removeClicked'
    },
    template: _.template(
      '<div class="col-sm-4">' +
        '<input class="form-control input-sm field-name" value="<%- name %>" />' +
      '</div>' +
      '<div class="col-sm-7">' +
        '<textarea class="form-control field-value"><%- value %></textarea>' +
        '<span class="hidden glyphicon glyphicon-remove form-control-feedback"></span>' +
      '</div>' +
      '<div class="col-sm-1">' +
        '<button class="plone-btn plone-btn-danger plone-btn-xs"><%- _t("Remove") %></button>' +
      '</div>')
  });


  var ResourceBoolFieldView = ResourceInputFieldView.extend({
    className: 'col-sm-offset-3 col-sm-9',
    template: _.template(
      '<div class="checkbox">' +
        '<label>' +
          '<input type="checkbox"> <%- title %></label>' +
      '</div>'),
    inputChanged: function(){
      if(this.$('input')[0].checked){
        this.options.registryData[this.options.name] = true;
      }else{
        this.options.registryData[this.options.name] = false;
      }
      $(document).trigger('resource-data-changed');
    },
    afterRender: function(){
      ResourceInputFieldView.prototype.afterRender.apply(this);
      if(this.options.value){
        this.$('input')[0].checked = true;
      }
    }
  });


  var ResourceListFieldView = ResourceInputFieldView.extend({
    sortable: false,
    template: _.template(
      '<label class="col-sm-3 control-label"><%- title %></label>' +
      '<ul class="col-sm-9 fields list-group" />' +
      '<button class="plone-btn plone-btn-default add pull-right"><%- _t("Add") %></button>'),
    events: {
      'click button.add': 'addRowClicked',
      'change input': 'inputChanged',
      'keyup input': 'textChanged',
      'click button.remove': 'removeItem'
    },

    initialize: function(options){
      ResourceInputFieldView.prototype.initialize.apply(this, [options]);
      if(!this.options.value){
        this.options.value = [];
      }
    },

    inputChanged: function(){
      var self = this;
      var data = [];
      self.$('input').each(function(){
        data.push($(this).val());
      });
      self.options.registryData[self.options.name] = self.options.value = data;
      $(document).trigger('resource-data-changed');
    },

    addRowClicked: function(e){
      var self = this;
      e.preventDefault();
      self.options.value.push('');
      self.render();
    },

    removeItem: function(e){
      e.preventDefault();
      var $el = $(e.target).parents('li');
      var index = $el.index();
      this.options.value.splice(index, 1);
      $el.remove();
    },

    afterRender: function(){
      ResourceInputFieldView.prototype.afterRender.apply(this);
      var self = this;
      var $container = self.$('.fields');
      _.each(self.options.value, function(value){
        $container.append('<li class="list-group-item"><div class="input-group">' +
          '<input class="form-control input-sm" value="' + value + '" />' +
          '<span class="input-group-btn">' +
            '<button class="plone-btn plone-btn-default remove plone-btn-sm">' + _t('Remove') + '</button></div></li>');
      });

      if(self.sortable){
        $container.addClass('pat-sortable');
        self.dd = new Sortable($container, {
          selector: 'li',
          dragClass: 'dragging',
          drop: function($el, delta) {
            if (delta !== 0){
              self.inputChanged();
            }
          }
        });
      }
    }
  });


  var ResourceSortableListFieldView = ResourceListFieldView.extend({
    sortable: true
  });


  var ResourceTextAreaFieldView = ResourceInputFieldView.extend({
    inputChanged: function(){
      this.options.registryData[this.options.name] = this.options.value = this.$('textarea').val();
    },
    template: _.template(
      '<label class="col-sm-3 control-label"><%- title %></label>' +
      '<div class="col-sm-9">' +
        '<textarea class="form-control input-sm" name="name"><%- value %></textarea>' +
      '</div>')
  });


  var ResourceSelectFieldView = ResourceInputFieldView.extend({
    events: {
      'change select': 'inputChanged'
    },
    inputChanged: function(){
      this.options.registryData[this.options.name] = this.options.value = this.$('.select').select2('val');
      $(document).trigger('resource-data-changed');
    },

    getSelectOptions: function(){
      return [];
    },

    serializedModel: function(){
      var self = this;
      return $.extend({}, {
        'options': self.getSelectOptions(),
        'description': ''
      }, self.options);
    },

    afterRender: function(){
      ResourceInputFieldView.prototype.afterRender.apply(this);
      var self = this;
      var values = self.options.value;
      var $select = self.$('.select');
      self.select2 = new Select2($select, {
        orderable: self.multiple,
        multiple: self.multiple,
        data: _.map(self.getSelectOptions(), function(val){
          return {id: val, text: val};
        })
      });
      $select.select2('val', values);
      $select.on('change', function(){
        self.inputChanged();
      });
    },

    template: _.template(
      '<label class="col-sm-3 control-label"><%- title %></label>' +
      '<div class="col-sm-9">' +
        '<input name="name" class="select" type="hidden" style="width: 100%" />' +
        '<%= description %>' +
      '</div>')
  });


  var BundleDependsFieldView = ResourceSelectFieldView.extend({
    getSelectOptions: function(){
      var self = this;
      return ['', '*'].concat(_.filter(_.keys(self.options.containerData), function(name){
        return name !== self.options.name;
      }));
    }
  });


  var BundleResourcesFieldView = ResourceSelectFieldView.extend({
    multiple: true,
    getSelectOptions: function(){
      var self = this;
      return _.sortBy(_.filter(_.keys(self.options.registryView.options.data.resources), function(name){
        return name !== self.options.name;
      }), function(item){
        return item.toLowerCase();
      });
    }
  });


  var ResourceNameFieldView = ResourceInputFieldView.extend({
    afterRender: function(){
      ResourceInputFieldView.prototype.afterRender.apply(this);
      this.$el.append('<span class="hidden glyphicon glyphicon-remove form-control-feedback"></span>');
    },

    handleError: function(error){
      if(error){
        this.$el.addClass('has-error').addClass('has-feedback');
        this.$('.form-control-feedback').removeClass('hidden');
      }else{
        this.$el.removeClass('has-error').removeClass('has-feedback');
        this.$('.form-control-feedback').addClass('hidden');
      }
    },

    inputChanged: function(){
      $(document).trigger('resource-data-changed');
      var value = this.$('input').val();
      if(value === this.resourceName){
        return this.handleError(false);
      }
      if(this.options.containerData[value] || !value){
        // already taken
        return this.handleError(true);
      }
      // move data
      var data = this.options.containerData[this.resourceName];
      this.options.containerData[value] = data;

      if(this.resourceName !== value){
        // and now delete old
        delete this.options.containerData[this.resourceName];
      }
      this.resourceName = this.options.value = this.options.form.options.name = this.options.form.name = value;

      if(this.options.parent){
        this.options.parent.options.name = value;
        this.options.parent.render();
      }
      if(this.options.form){
        this.options.form.$('h3').html(value);
      }
      return this.handleError(false);
    },
    serializedModel: function(){
      var data = $.extend({}, {
        description: ''
      }, this.options);
      data.value = this.options.resourceName;
      return data;
    }
  });

  return {
    ResourceDisplayFieldView: ResourceDisplayFieldView,
    VariableFieldView: VariableFieldView,
    ResourceInputFieldView: ResourceInputFieldView,
    ResourceNameFieldView: ResourceNameFieldView,
    ResourceSortableListFieldView: ResourceSortableListFieldView,
    ResourceTextAreaFieldView: ResourceTextAreaFieldView,
    BundleResourcesFieldView: BundleResourcesFieldView,
    BundleDependsFieldView: BundleDependsFieldView,
    ResourceBoolFieldView: ResourceBoolFieldView,
    PatternFieldView: PatternFieldView
  };
});
