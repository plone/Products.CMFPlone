/* Resource Registry pattern.
 *
 * Options:
 *    bundles(object): object with all bundles ({})
 *    resources(object): object with all resources ({})
 *    javascripts(object): object with all legacy type javascripts ({})
 *    css(object): object with all legacy type css ({}) 
 *    overrides(array): List of current overrides ([])
 *    managerUrl(string): url to handle manage actions(null)
 *    baseUrl(string): to render resources from(null)
 *    lesscUrl(string): url to lessc to load for compiling less(null)
 *    rjsUrl(string): url to lessc to load for compiling less(null)
 *    lessvariables(object): group of settings that can be configured({})
 *
 *
 * Documentation:
 *    # Defaults
 *
 *    {{ example-1 }}
 *
 *
 * Example: example-1
 *    <div class="pat-resourceregistry"
 *        data-pat-resourceregistry='{"bundles":{
 *                                     "plone": {
 *                                       "resources": ["plone"], "depends": "",
 *                                       "expression": "", "enabled": true, "conditionalcomment": "",
 *                                       "develop_javascript": false, "develop_css": false,
 *                                       "compile": true
 *                                     },
 *                                     "plone-auth": {
 *                                       "resources": ["plone-auth"], "depends": "plone",
 *                                       "expression": "", "enabled": true, "conditionalcomment": "",
 *                                       "develop_javascript": false, "develop_css": false,
 *                                       "compile": true
 *                                     },
 *                                     "barceloneta": {
 *                                       "resources": ["barceloneta"], "depends": "*",
 *                                       "expression": "", "enabled": true, "conditionalcomment": "",
 *                                       "develop_javascript": false, "develop_css": false,
 *                                       "compile": false
 *                                     }
 *                                   },
 *                                   "resources": {
 *                                     "plone": {
 *                                       "url": "js/bundles", "js": "plone.js",
 *                                       "css": [], "deps": "", "export": "",
 *                                       "conf": "", "force": false
 *                                     },
 *                                     "plone-auth": {
 *                                       "url": "js/bundles", "js": "plone-auth.js",
 *                                       "css": [], "deps": "", "export": "",
 *                                       "conf": "", "force": false
 *                                     },
 *                                     "barceloneta": {
 *                                       "url": "js/bundles", "js": "barceloneta.js",
 *                                       "css": ["barceloneta.less"], "deps": "", "export": "",
 *                                       "conf": "", "force": false
 *                                     },
 *                                     "modal": {
 *                                       "url": "patterns/modal", "js": "pattern.js",
 *                                       "css": ["pattern.modal.less"], "deps": "", "export": "",
 *                                       "conf": "", "force": false
 *                                     },
 *                                     "autotoc": {
 *                                       "url": "patterns/autotoc", "js": "pattern.js",
 *                                       "css": ["pattern.autotoc.less", "pattern.other.less"],
 *                                       "deps": "", "export": "", "conf": ""
 *                                     },
 *                                     "pickadate": {
 *                                       "url": "patterns/pickadate", "js": "pattern.js",
 *                                       "css": ["pattern.pickadate.less"], "deps": "", "export": "",
 *                                       "conf": "", "force": true
 *                                     }
 *                                   },
 *                                   "lessvariables": {
 *                                     "foo": "bar"
 *                                   },
 *                                   "overrides": ["patterns/pickadate/pattern.js"],
 *                                   "baseUrl": "/resources-registry",
 *                                   "manageUrl": "/registry-manager",
 *                                   "lessUrl": "node_modules/less/dist/less-1.7.4.min.js",
 *                                   "lessConfigUrl": "tests/files/lessconfig.js",
 *                                   "rjsUrl": "tests/files/r.js"}'>
 *    </div>
 *
 */

define([
  'jquery',
  'mockup-patterns-base',
  'underscore',
  'mockup-ui-url/views/base',
  'mockup-utils',
  'mockup-patterns-resourceregistry-url/js/less',
  'mockup-patterns-resourceregistry-url/js/overrides',
  'mockup-patterns-resourceregistry-url/js/registry',
  'mockup-patterns-resourceregistry-url/js/patternoptions',
  'translate'
], function($, Base, _, BaseView, utils, LessVariablesView,
            OverridesView,RegistryView, PatternOptionsView, _t) {
  'use strict';


  var TabView = BaseView.extend({
    tagName: 'div',
    activeTab: 'registry',
    template: _.template('' +
      '<div class="autotabs">' +
        '<ul class="main-tabs autotoc-nav" role="tablist">' +
          '<li class="registry-btn"><a href="#"><%- _t("Registry") %></a></li>' +
          '<li class="overrides-btn"><a href="#"><%- _t("Overrides") %></a></li>' +
          '<li class="lessvariables-btn"><a href="#"><%- _t("Less Variables") %></a></li>' +
          '<li class="patternoptions-btn"><a href="#"><%- _t("Pattern Options") %></a></li>' +
        '</ul>' +
      '</div>' +
      '<div class="tab-content" />'
    ),
    events: {
      'click .registry-btn a': 'hideShow',
      'click .overrides-btn a': 'hideShow',
      'click .lessvariables-btn a': 'hideShow',
      'click .patternoptions-btn a': 'hideShow'
    },
    hideShow: function(e){
      var self = this;
      if(e !== undefined){
        e.preventDefault();
        self.activeTab = $(e.target).parent()[0].className.replace('-btn', '');
      }
      self.$('.main-tabs > li a').removeClass('active');
      self.$content.find('.tab-pane').removeClass('active');
      self.tabs[self.activeTab].btn.find('a').addClass('active');
      self.tabs[self.activeTab].content.addClass('active');
    },
    initialize: function(options) {
      var self = this;

      BaseView.prototype.initialize.apply(self, [options]);
      self.registryView = new RegistryView({
        data: options,
        tabView: self});
      self.overridesView = new OverridesView({
        data: options,
        tabView: self});
      self.lessvariablesView = new LessVariablesView({
        data: options,
        tabView: self});
      self.patternoptionsView = new PatternOptionsView({
        data: options,
        tabView: self});
      self.tabs = {};
    },

    render: function(){
      var self = this;
      self.$el.append(self.template({_t: _t}));
      self.loading = new utils.Loading();
      self.$tabs = self.$('ul.main-tabs');
      self.$content = self.$('.tab-content');
      self.$content.append(self.registryView.render().el);
      self.$content.append(self.overridesView.render().el);
      self.$content.append(self.lessvariablesView.render().el);
      self.$content.append(self.patternoptionsView.render().el);
      self.tabs = {
        registry: {
          btn: self.$('.registry-btn'),
          content: self.registryView.$el
        },
        overrides: {
          btn: self.$('.overrides-btn'),
          content: self.overridesView.$el
        },
        lessvariables: {
          btn: self.$('.lessvariables-btn'),
          content: self.lessvariablesView.$el
        },
        patternoptions: {
          btn: self.$('.patternoptions-btn'),
          content: self.patternoptionsView.$el
        }
      };
      self.hideShow();
      return self;
    },

    saveData: function(action, data, onSave, onError){
      var self = this;
      self.loading.show();
      if(!data){
        data = {};
      }
      data = $.extend({}, data, {
        action: action,
        _authenticator: utils.getAuthenticator()
      });
      $.ajax({
        url: self.options.manageUrl,
        type: 'POST',
        dataType: 'json',
        data: data
      }).done(function(resp){
        if(onSave){
          onSave(resp);
        }
        if(resp.success !== undefined && !resp.success && resp.msg){
          window.alert(resp.msg);
        }
      }).always(function(){
        self.loading.hide();
      }).fail(function(resp){
        if(onError){
          onError(resp);
        }else{
          window.alert(_t('Error processing ajax request for action: ') + action);
        }
      });
    }
  });


  var ResourceRegistry = Base.extend({
    name: 'resourceregistry',
    trigger: '.pat-resourceregistry',
    defaults: {
      bundles: {},
      resources: {},
      javascripts: {},
      css: {},
      overrides: [],
      manageUrl: null,
      baseUrl: null,
      rjsUrl: null,
      lessvariables: {},
      patternoptions: {}
    },
    init: function() {
      var self = this;
      self.$el.empty();
      self.tabs = new TabView(self.options);
      self.$el.append(self.tabs.render().el);
    }
  });

  return ResourceRegistry;

});
