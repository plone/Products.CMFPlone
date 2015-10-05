/*
 * much of this code is heavily barrowed from Rok Garbas's iframe
 * code that has since been removed from mockup
 */

define([
  'jquery'
], function($) {
  'use strict';

  window.IFrame = function(options) { this.init(options); };
  window.IFrame.prototype = {
    defaults: {
      doctype: '<!doctype html>',
      title: '',
      name: '',
      resources: [],
      callback: function(){},
      configure: function(){},
      onLoad: function(){}
    },

    init: function(options) {
      var self = this;
      self.options = $.extend({}, self.defaults, options);

      // register this guy
      if(!window.iframe){
        window.iframe = {};
      }
      window.iframe[self.options.name] = self;

      self.loaded = false;

      // Create iframe
      var iframe = window.document.createElement('iframe');

      iframe.setAttribute('id', self.options.name);
      iframe.setAttribute('name', self.options.name);
      iframe.setAttribute('style', 'display:none;');
      iframe.setAttribute('src', 'javascript:false');

      window.document.body.appendChild(iframe);
      self.el = iframe;
      self.window = iframe.contentWindow;
      self.document = self.window.document;

      self.options.configure(self);

      var resourcesData = '';
      for(var i=0; i<self.options.resources.length; i=i+1){
        var url = self.options.resources[i];
        var resource;
        if (url.slice( -3 ) === '.js') {
          resource = window.document.createElement('script');
          resource.src = url;
          resource.type = 'text/javascript';
          resource.async = false;
        } else if (url.slice( -4 ) === '.css') {
          resource = window.document.createElement('link');
          resource.href = url;
          resource.type = 'text/css';
          resource.rel = 'stylesheet';
        } else if (url.slice( -5 ) === '.less') {
          resource = window.document.createElement('link');
          resource.href = url;
          resource.type = 'text/css';
          resource.rel = 'stylesheet/less';
        }
        resourcesData += '\n' + resource.outerHTML;
      }

      self.document.open();
      self.document.write(
          self.options.doctype +
          '<html>' +
            '<head>' +
              '<title>' + self.options.title + '</title>' +
              '<meta http-equiv="X-UA-Compatible" content="IE=edge">' +
            '</head>' +
            '<body onload="parent.window.iframe[\'' +
                self.options.name + '\'].load()">' +
              resourcesData +
            '</body>' +
          '</html>'
      );
      self.document.close();
    },

    load: function() {
      var self = this;

      // check if already loaded
      if ( self.loaded === true ) {
        return;
      }

      // mark iframe as loaded
      self.loaded = true;

      self.options.onLoad(self);
    },
    destroy: function(){
      delete window.iframe[this.options.name];
      window.document.body.removeChild(this.el);
    }
  };

  return window.IFrame;
});
