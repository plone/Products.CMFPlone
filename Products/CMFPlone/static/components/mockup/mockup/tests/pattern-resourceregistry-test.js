define([
  'sinon',
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-resourceregistry'
], function(sinon, expect, $, registry, ResourceRegistry) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  describe('Resource registry', function() {
    beforeEach(function() {
      var testData = {"bundles":{
                        "plone": {
                          "resources": "plone", "depends": null,
                          "expression": "", "enabled": true, "conditionalcomment": "",
                          "develop_javascript": false, "develop_css": false, "compile": true
                        },
                        "plone-auth": {
                          "resources": "plone-auth", "depends": "plone",
                          "expression": "", "enabled": true, "conditionalcomment": "",
                          "develop_javascript": false, "develop_css": false, "compile": true
                        },
                        "barceloneta": {
                          "resources": "plone", "depends": "*",
                          "expression": "", "enabled": true, "conditionalcomment": "",
                          "develop_javascript": false, "develop_css": false, "compile": true
                        }
                      },
                      "resources": {
                        "plone": {
                          "url": "++plone++js/bundles", "js": "plone.js",
                          "css": [], "deps": "", "export": "",
                          "conf": "", "force": false
                        },
                        "plone-auth": {
                          "url": "++plone++js/bundles", "js": "plone-auth.js",
                          "css": [], "deps": "", "export": "",
                          "conf": "", "bundle": false
                        },
                        "barceloneta": {
                          "url": "++plone++js/bundles", "js": "barceloneta.js",
                          "css": ["barceloneta.less"], "deps": "", "export": "",
                          "conf": "", "bundle": false
                        },
                        "modal": {
                          "url": "patterns/modal", "js": "pattern.js",
                          "css": ["pattern.modal.less"], "deps": "", "export": "",
                          "conf": "", "bundle": false
                        },
                        "autotoc": {
                          "url": "patterns/autotoc", "js": "pattern.js",
                          "css": ["pattern.autotoc.less", "pattern.other.less"],
                          "deps": "", "export": "", "conf": "", "enabled": true
                        },
                        "pickadate": {
                          "url": "patterns/pickadate", "js": "pattern.js",
                          "css": ["pattern.pickadate.less"], "deps": "", "export": "",
                          "conf": "", "enabled": true
                        }
                      },
                      "overrides": ["patterns/pickadate/pattern.js"],
                      "baseUrl": "/resources-registry",
                      "overrideManageUrl": "/resource-override-manager",
                      "saveUrl": "/"};
      this.$el = $('' +
        '<div>' +
        '  <div class="pat-resourceregistry "' +
        '  </div>' +
        '</div>');

      this.$pat =  this.$el.find('.pat-resourceregistry');
      this.pat = new ResourceRegistry(this.$pat, testData);
    });
    afterEach(function() {
      this.$el.remove();
    });

    it('loads', function() {
      expect(this.$el.find('ul.bundles li').length).to.equal(4);
      expect(this.$el.find('ul.resources li').length).to.equal(6);
    });

    it('customize resource', function(){
      this.pat.tabs.showOverrides = true;
      this.pat.tabs.hideShow();
      this.$el.find('.select').select2('val', 'plone', true);
      expect(this.pat.options.overrides.length).to.equal(2);
    });

    it('loads resource data', function(){
      this.$pat.find('.resource-list-item-autotoc a').trigger('click');
      expect(this.$pat.find('.resource-entry .field-url input').attr('value')).to.equal('patterns/autotoc');
    });

    it('loads bundle data', function(){
      this.$pat.find('.bundle-list-item-plone a').trigger('click');
      expect(this.$pat.find('.resource-entry .field-resources input').length).to.equal(2);
    });

    it('edit resource data', function(){
      this.$pat.find('.resource-list-item-autotoc a').trigger('click');
      this.$pat.find('.resource-entry .field-css input').attr('value', 'foobar').trigger('change');
      expect(this.pat.options.resources.autotoc.url).to.equal('patterns/autotoc');
    });

    it('edit bundle data', function(){
      this.$pat.find('.bundle-list-item-plone a').trigger('click');
      this.$pat.find('.resource-entry .field-expression input').attr('value', 'foobar').trigger('change');
      expect(this.pat.options.bundles.plone.expression).to.equal('foobar');
    });

    it('delete resource', function(){
      window.confirm = function() { return true; };
      this.$pat.find('.resource-list-item-autotoc button').trigger('click');
      expect(this.pat.options.resources.autotoc).to.equal(undefined);
    });

    it('delete bundle', function(){
      window.confirm = function() { return true; };
      this.$pat.find('.bundle-list-item-plone button').trigger('click');
      expect(this.pat.options.bundles.plone).to.equal(undefined);
    });

    it('delete customization', function(){

    });

    it('add resource', function(){
      this.$pat.find('button.add-resource').trigger('click');
      expect(this.$el.find('ul.resources li').length).to.equal(7);
    });

    it('add bundle', function(){
      this.$pat.find('button.add-bundle').trigger('click');
      expect(this.$el.find('ul.bundles li').length).to.equal(5);
    });

  });

});