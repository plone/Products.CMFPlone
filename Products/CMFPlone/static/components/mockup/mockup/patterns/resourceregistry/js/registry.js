define([
  'jquery',
  'underscore',
  'mockup-ui-url/views/base',
  'mockup-utils',
  'mockup-patterns-resourceregistry-url/js/fields',
  'mockup-patterns-resourceregistry-url/js/builder',
  'translate'
], function($, _, BaseView, utils, fields, Builder, _t) {
  'use strict';

  var AbstractResourceEntryView = BaseView.extend({
    tagName: 'div',
    className: 'resource-entry',
    template: _.template(
      '<h3><%- name %></h3>' +
      '<div class="panel-body form-horizontal">' +
      '</div>'
    ),

    serializedModel: function(){
      return $.extend({}, {name: this.name}, this.options);
    },

    afterRender: function(){
      var self = this;
      var $body = self.$('.panel-body');
      self.$el.addClass(self.name + '-resource-entry');
      _.each(self.fields, function(field){
        var options = $.extend({}, field, {
          value: self.options.data[field.name],
          registryData: self.options.data,
          containerData: self.options.containerData,
          resourceName: self.options.name,
          registryView: self.options.registryView,
          parent: self.options.parent,
          form: self
        });
        if(!options.value){
          options.value = '';
        }
        var View = field.view;
        if(!View){
          View = fields.ResourceInputFieldView;
        }
        $body.append((new View(options)).render().el);
      });
    }
  });


  var ResourceEntryView = AbstractResourceEntryView.extend({
    fields: [{
      name: 'name',
      title: _t('Name'),
      view: fields.ResourceNameFieldView
    }, {
      name: 'url',
      title: _t('URL'),
      description: _t('Resources base URL')
    }, {
      name: 'js',
      title: _t('JS'),
      description: _t('Main JavaScript file')
    }, {
      name: 'css',
      title: _t('CSS/LESS'),
      description: _t('List of CSS/LESS files to use for resource'),
      view: fields.ResourceSortableListFieldView
    },{
      name: 'init',
      title: _t('Init'), 
      description: _t('Init instruction for requirejs shim')
    }, {
      name: 'deps',
      title: _t('Dependencies'),
      description: _t('Comma-separated values of resources for requirejs shim')
    }, {
      name: 'export',
      title: _t('Export'),
      description: _t('Export vars for requirejs shim')
    }, {
      name: 'conf',
      title: _t('Configuration'),
      description: _t('Configuration in JSON for the widget'),
      view: fields.ResourceTextAreaFieldView
    }]
  });


  var BundleEntryView = AbstractResourceEntryView.extend({
    fields: [{
      name: 'name',
      title: _t('Name'),
      view: fields.ResourceNameFieldView
    }, {
      name: 'resources',
      title: _t('Resources'),
      description: _t('A main resource file to bootstrap bundle or a list of resources to load.'),
      view: fields.BundleResourcesFieldView
    }, {
      name: 'depends',
      title: _t('Depends'),
      description: _t('Bundle this depends on'),
      view: fields.BundleDependsFieldView
    }, {
      name: 'expression',
      title: _t('Expression'),
      description: _t('Conditional expression to decide if this resource will run')
    }, {
      name: 'enabled',
      title: _t('Enabled'),
      view: fields.ResourceBoolFieldView
    }, {
      name: 'conditionalcomment',
      title: _t('Conditional comment'),
      description: _t('Internet Explorer conditional comment')
    }, {
      name: 'compile',
      title: _t('Does your bundle contain any RequireJS or LESS files?'),
      view: fields.ResourceBoolFieldView
    }, {
      name: 'last_compilation',
      title: _t('Last compilation'),
      description: _t('Date/Time when your bundle was last compiled. Empty, if it was never compiled.'),
      view: fields.ResourceDisplayFieldView
    }, {
      name: 'jscompilation',
      title: _t('Compiled JavaScript'),
      description: _t('Automatically generated path to the compiled JavaScript.'),
      view: fields.ResourceDisplayFieldView
    }, {
      name: 'csscompilation',
      title: _t('Compiled CSS'),
      description: _t('Automatically generated path to the compiled CSS.'),
      view: fields.ResourceDisplayFieldView
    }]
  });


  var RegistryResourceListItem = BaseView.extend({
    tagName: 'li',
    type: 'resource',
    className: 'list-group-item',
    template: _.template(
      '<a href="#"><%- name %></a> ' +
      '<button class="pull-right plone-btn plone-btn-danger delete plone-btn-xs"><%- _t("Delete") %></button>'
    ),
    events: {
      'click a': 'editResource',
      'click button.delete': 'deleteClicked'
    },
    defaults: {
      develop_javascript: false,
      develop_css: false,
      compile: true
    },
    afterRender: function(){
      this.$el.attr('data-name', this.options.name);
      this.$el.addClass(this.type + '-list-item-' + this.options.name);
    },
    serializedModel: function(){
      return $.extend({}, this.defaults, {
        name: this.options.name,
        view: this.options.registryView
      }, this.options.data);
    },
    editResource: function(e){
      if(e){
        e.preventDefault();
      }
      var options = $.extend({}, this.options, {
        containerData: this.options.registryView.options.data.resources,
        parent: this
      });
      var resource = new ResourceEntryView(options);
      this.registryView.showResourceEditor(resource, this, 'resource');

      // and scroll to resource since huge list makes this hard to notice
      $('html, body').animate({
        scrollTop: resource.$el.offset().top
      }, 1000);
    },
    deleteClicked: function(e){
      e.preventDefault();
      if(window.confirm(_t('Are you sure you want to delete the ${name} resource?', {name: this.options.name}))){
        delete this.options.registryView.options.data.resources[this.options.name];
        this.options.registryView.dirty = true;
        if(this.options.registryView.activeResource &&
           this.options.registryView.activeResource.resource.name === this.options.name){
          this.options.registryView.activeResource = null;
        }
        this.options.registryView.render();
      }
    }
  });


  var RegistryBundleListItem = RegistryResourceListItem.extend({
    type: 'bundle',
    active: false,
    template: _.template(
      '<a href="#"><%- name %></a> ' +
      '<div class="actions">' +
        '<div class="plone-btn-group">' +
          '<% if(view.options.data.development) { %>' +
            '<% if(develop_javascript){ %>' +
              '<button class="plone-btn plone-btn-warning on develop-js plone-btn-xs"><%- _t("Stop Developing JavaScript") %></button>' +
            '<% } else { %>' +
              '<button class="plone-btn plone-btn-default develop-js plone-btn-xs"><%- _t("Develop JavaScript") %></button>' +
            '<% } %>' +
            '<% if(develop_css){ %>' +
              '<button class="plone-btn plone-btn-warning on develop-css plone-btn-xs"><%- _t("Stop Developing CSS") %></button>' +
            '<% } else { %>' +
              '<button class="plone-btn plone-btn-default develop-css plone-btn-xs"><%- _t("Develop CSS") %></button>' +
            '<% } %>' +
          '<% } %>' +
          '<% if(compile){ %>' +
            '<button class="plone-btn plone-btn-default build plone-btn-xs"><%- _t("Build") %></button>' +
          '<% } %>' +
          '<button class="plone-btn plone-btn-danger delete plone-btn-xs"><%- _t("Delete") %></button>' +
        '</div>' +
      '</div>'
    ),
    events: $.extend({}, RegistryResourceListItem.prototype.events, {
      'click button.build': 'buildClicked',
      'click button.develop-js': 'developJavaScriptClicked',
      'click button.develop-css': 'developCSSClicked'
    }),
    developJavaScriptClicked: function(e){
      e.preventDefault();
      this.options.data.develop_javascript = !this.options.data.develop_javascript;
      this.options.registryView.dirty = true;
      this.options.registryView.render();
    },
    developCSSClicked: function(e){
      e.preventDefault();
      this.options.data.develop_css = !this.options.data.develop_css;
      this.options.registryView.dirty = true;
      this.options.registryView.render();
    },
    afterRender: function(){
      RegistryResourceListItem.prototype.afterRender.apply(this);
      if(this.active){
        this.editResource();
      }
    },
    editResource: function(e){
      if(e){
        e.preventDefault();
      }
      var options = $.extend({}, this.options, {
        containerData: this.options.registryView.options.data.bundles
      });
      var resource = new BundleEntryView(options);
      this.registryView.showResourceEditor(resource, this, 'bundle');

      // only one can be edited at a time, deactivate
      _.each(this.options.registryView.items.bundles, function(bundleItem){
        bundleItem.active = false;
      });
      this.active = true;
      this.$el.parent().find('.list-group-item').removeClass('active');
      this.$el.addClass('active');
    },
    deleteClicked: function(e){
      e.preventDefault();
      if(window.confirm(_t('Are you sure you want to delete the ${name} bundle?', {name: this.options.name}))){
        delete this.options.registryView.options.data.bundles[this.options.name];
        this.options.registryView.dirty = true;
        if(this.options.registryView.activeResource &&
           this.options.registryView.activeResource.resource.name === this.options.name){
          this.options.registryView.activeResource = null;
        }
        this.options.registryView.render();
      }
    },
    
    buildClicked: function(e){
      e.preventDefault();
      var self = this;
      if(this.options.registryView.dirty){
        window.alert(_t('You have unsaved changes. Save or discard before building.'));
      }else{
        var builder = new Builder(self.options.name, self);
        builder.run();
      }
    }
  });

  var BaseResourcesPane = BaseView.extend({
    tagName: 'div',
    className: 'tab-pane',
    $form: null,
    activeResource: null,

    initialize: function(options) {
      var self = this;
      BaseView.prototype.initialize.apply(self, [options]);
      self.previousData = self._copyData();
      /* setup scroll spy to move form into view if necessary */
      /* disabled, at least for now, forms too bad to do this with...
      $(window).scroll(function(){
        if(self.$form){
          var offset = self.$el.parent().offset();
          var top = $(document).scrollTop();
          if(top > offset.top){
            self.$form.css({marginTop: top - offset.top});
          }else{
            self.$form.css({marginTop: null});
          }
        }
      });
      */
    },

    showResourceEditor: function(resource, view, type){
      this.activeResource = {
        resource: resource,
        item: view,
        type: type
      };
      this.$form.empty().append(resource.render().el);
    },

    _copyData: function(){
      return $.extend(true, {}, this.options.data);
    },

    _revertData: function(data){
      this.options.data = $.extend(true, {}, data);
    },

    revertChanges: function(e){
      if(e){
        e.preventDefault();
      }
      if(window.confirm(_t('Are you sure you want to cancel? You will lose all changes.'))){
        this._revertData(this.previousData);
        this.activeResource = null;
        this.render();
      }
    },
    afterRender: function(){
      this.$form = this.$('.form');
      this.loading = this.options.tabView.loading;
    }
  });


  var RegistryView = BaseResourcesPane.extend({
    template: _.template(
      '<div class="buttons-container">' +
        '<div class="plone-btn-group pull-right">' +
          '<button class="plone-btn plone-btn-primary save"><%- _t("Save") %></button>' +
          '<button class="plone-btn plone-btn-default cancel"><%- _t("Cancel") %></button>' +
        '</div>' +
        '<div class="plone-btn-group pull-right">' +
          '<button class="plone-btn plone-btn-default add-bundle"><%- _t("Add bundle") %></button>' +
          '<button class="plone-btn plone-btn-default add-resource"><%- _t("Add resource") %></button>' +
        '</div>' +
      '</div>' +
      '<div class="row">' +
        '<div class="checkbox development-mode">' +
          '<label>' +
            '<input type="checkbox" ' +
              '<% if(data.development){ %> checked="checked" <% } %>' +
              ' > <%- _t("Development Mode(only logged in users)") %>' +
          '</label>' +
        '</div>' +
      '</div>' +
      '<div class="row">' +
        '<div class="items col-md-5">' +
          '<ul class="bundles list-group">' +
            '<li class="list-group-item list-group-item-warning"><%- _t("Bundles") %></li>' +
          '</ul>' +
          '<ul class="resources-header list-group">' +
            '<li class="list-group-item list-group-item-warning"><%- _t("Resources") %> ' +
              '<input class="float-right form-control input-xs" ' +
                      'placeholder="<%- _t("Filter...") %>" />' +
            '</li>' +
          '</ul>' +
          '<ul class="resources list-group">' +
          '</ul>' +
        '</div>' +
        '<div class="form col-md-7"></div>' +
      '</div>'),
    events: {
      'click button.save': 'saveClicked',
      'click button.add-resource': 'addResourceClicked',
      'click button.add-bundle': 'addBundleClicked',
      'click button.cancel': 'revertChanges',
      'keyup .resources-header input': 'filterResources',
      'change .development-mode input': 'developmentModeChanged'
    },
    filterTimeout: 0,
    dirty: false,

    initialize: function(options){
      var self = this;
      BaseResourcesPane.prototype.initialize.apply(self, [options]);
      $(document).on('resource-data-changed', function(){
        self.dirty = true;
        self.showHideButtons();
      });
    },

    showHideButtons: function(){
      var val = true;
      if(this.dirty){
        val = false;
      }
      this.$('button.save').prop('disabled', val);
      this.$('button.cancel').prop('disabled', val);
    },

    filterResources: function(){
      var self = this;
      if(self.filterTimeout){
        clearTimeout(self.filterTimeout);
      }
      self.filterTimeout = setTimeout(function(){
        var filterText = self.$('.resources-header input').val().toLowerCase();
        var $els = self.$('.resources .list-group-item');
        if(!filterText || filterText.length < 3){
          $els.removeClass('hidden');
        }else{
          $els.each(function(){
            var $el = $(this);
            if($el.find('a').html().toLowerCase().indexOf(filterText) !== -1){
              $el.removeClass('hidden');
            }else{
              $el.addClass('hidden');
            }
          });
        }
      }, 200);
    },

    _copyData: function(){
      return $.extend(true, {}, {
        bundles: this.options.data.bundles,
        resources: this.options.data.resources
      });
    },

    _revertData: function(data){
      this.options.data.bundles = $.extend(true, {}, data.bundles);
      this.options.data.resources = $.extend(true, {}, data.resources);
      this.dirty = false;
    },

    afterRender: function(){
      var self = this;
      self.showHideButtons();
      self.$bundles = self.$('ul.bundles');
      self.$resources = self.$('ul.resources');
      var data = self.options.data;
      var bundles = _.sortBy(_.keys(data.bundles), function(v){ return v.toLowerCase(); });
      self.items = {
        bundles: {},
        resources: {}
      };
      _.each(bundles, function(resourceName){
        var item;
        if(self.activeResource && self.activeResource.type === 'bundle' && self.activeResource.item.options.name === resourceName){
          item = self.activeResource.item;
        }else{
          item = new RegistryBundleListItem({
            data: data.bundles[resourceName],
            name: resourceName,
            registryView: self});
        }
        self.items.bundles[resourceName] = item;
        self.$bundles.append(item.render().el);
      });
      var resources = _.sortBy(_.keys(data.resources), function(v){ return v.toLowerCase(); });
      _.each(resources, function(resourceName){
        var item;
        if(self.activeResource && self.activeResource.type === 'resource' && self.activeResource.item.options.name === resourceName){
          item = self.activeResource.item;
        } else {
          item = new RegistryResourceListItem({
            data: data.resources[resourceName],
            name: resourceName,
            registryView: self});
        }
        self.items.resources[resourceName] = item;
        self.$resources.append(item.render().el);
      });
      BaseResourcesPane.prototype.afterRender.apply(self);

      // finally, show edit pane if there is an active resource
      if(self.activeResource){
        self.showResourceEditor(self.activeResource.resource, self.activeResource.item, self.activeResource.type);
      }
      return self;
    },

    addResourceClicked: function(e){
      e.preventDefault();
      var name = utils.generateId('new-resource-');
      this.options.data.resources[name] = {
        enabled: true
      };
      this.dirty = true;
      this.render();
      this.items.resources[name].editResource();
    },

    addBundleClicked: function(e){
      e.preventDefault();
      var name = utils.generateId('new-bundle-');
      this.options.data.bundles[name] = {
        enabled: true
      };
      this.dirty = true;
      this.render();
      this.items.bundles[name].editResource();
    },

    saveClicked: function(e){
      var self = this;
      e.preventDefault();
      self.options.tabView.saveData('save-registry', {
        resources: JSON.stringify(self.options.data.resources),
        bundles: JSON.stringify(self.options.data.bundles),
        development: self.options.data.development && 'true' || 'false'
      }, function(){
        self.dirty = false;
        var activeResource = self.activeResource;
        self.activeResource = null;
        self.previousData = self._copyData();
        self.render();
        if(activeResource){
          var name = activeResource.resource.name;
          self.options.data.resources[name] = {
            enabled: true
          };
          if(activeResource.type === 'bundle'){
            self.items.bundles[name].editResource();
          }else{
            self.items.resources[name].editResource();
          }
        }
      });
    },

    developmentModeChanged: function(){
      var self = this;
      if(self.$('.development-mode input')[0].checked){
        this.options.data.development = true;
      }else{
        this.options.data.development = false;
      }
      this.dirty = true;
      this.render();
    }
  });

  return RegistryView;

});
