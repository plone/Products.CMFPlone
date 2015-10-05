
define([
  'jquery',
  'mockup-patterns-modal',
  'underscore',
  'mockup-utils',
  'mockup-patterns-resourceregistry-url/js/iframe',
  'translate'
], function($, Modal, _, utils, IFrame, _t){
  'use strict';

  var Builder = function(bundleName, bundleListItem){
    var self = this;
    self.bundleName = bundleName;
    self.bundleListItem = bundleListItem;
    self.rview = bundleListItem.options.registryView;
    self.$results = null;
    self.$btnClose = null;

    self.rview.loading.show();
    self.modal = new Modal($('<div/>').appendTo(self.rview.$el), {
      html: _.template('<div id="content">' +
        '<h1>Bundle Builder</h1>' +
        '<div class="start-info"><p>You are about to build the <span class="label label-primary">' +
          '<%= name %></span> pattern. </p><p>This may take some a bit of time so ' +
          'we will try to keep you updated on the progress.</p><p> Press the "Build it" ' +
          'button to proceed.</p></div>' +
        '<ul class="list-group hidden"></ul>' +
        '<button class="plone-btn plone-btn-default cancel hidden cancel-build"><%- _t("Close") %></button>' +
        '<button class="plone-btn plone-btn-primary build"><%- _t("Build it") %></button>' +
      '</div>', $.extend({ _t: _t }, bundleListItem.options)),
      content: null,
      width: 500,
      buttons: '.plone-btn'
    });
    self.modal.on('shown', function() {
      var $el = self.modal.$modal;
      var $info = $el.find('.start-info');
      self.$btnClose = $el.find('button.cancel-build');
      var $btn = $el.find('button.build');
      $btn.off('click').on('click', function(e){
        e.preventDefault();
        $info.addClass('hidden');
        $btn.prop('disabled', true);
        self.$results = $el.find('.list-group').removeClass('hidden');
        self.buildJS();
        self.rview.loading.show();
      });

      self.$btnClose.off('click').on('click', function(){
        self.modal.hide();
      });
    });

    self.addResult = function(txt, klass){
      if(!klass){
        klass = '';
      }
      self.$results.append('<li class="list-group-item ' + klass + '">' + txt + '</li>');
    };

    self.run = function(){
      self.modal.show();
    };

    self.finished = function(error){
      var msg = _t('Finished!');
      if(error){
        msg = _t('Error in build process');
      }
      self.addResult(msg, 'list-group-item-warning');
      self.$btnClose.removeClass('hidden');
      self.rview.loading.hide();
    };

    self.buildJS = function(){
      self.addResult(_t('building javascripts'));
      $.ajax({
        url: self.rview.options.data.manageUrl,
        type: 'POST',
        dataType: 'json',
        data: {
          action: 'js-build-config',
          bundle: self.bundleName,
          _authenticator: utils.getAuthenticator()
        },
        success: function(data){
          /* sort of weird here, follow along. We'll build CSS after JS */
          self._buildJSBundle(data);
        },
        error: function(){
          self.addResult(_t('Error building resources'));
          self.finished(true);
        }
      });
    };

    self._buildCSSBundle = function(config){
      var iframe = new IFrame({
        name: 'lessc',
        resources: config.less.concat([
          self.rview.options.data.lessConfigUrl,
          self.rview.options.data.lessUrl]),
        configure: function(iframe){
          iframe.window.lessErrorReporting = function(what, error, href){
            if(what !== 'remove'){
              self.addResult(_t('less compilation error on file ') + href + ': ' + error);
            }
          };
        }
      });

      /* XXX okay, wish there were a better way,
         but we need to pool to find the out if it's down loading less */
      self.addResult(config.less.length + _t(' css files to build'));
      var lessModified = Boolean(
          self.rview.options.data.lessModifyUrl === null ||
          self.rview.options.data.lessModifyUrl === undefined
      );
      var checkFinished = function(){
        var $styles =  $('style[type="text/css"][id]', iframe.document);
        for(var i=0; i<$styles.length; i=i+1){
          var $style = $styles.eq(i);
          if($style.attr('id') === 'less:error-message'){
            self.addResult(_t('Error compiling less'));
            return self.finished(true);
          }
        }
        if($styles.length === config.less.length && lessModified === true){
          // we're finished, save it
          var data = {};
          $styles.each(function(){
            var $el = $(this);
            data['data-' + $el.attr('id')] = $el.html();
          });
          iframe.destroy();
          $.ajax({
            url: self.rview.options.data.manageUrl,
            type: 'POST',
            dataType: 'json',
            data: $.extend(data, {
              action: 'save-less-build',
              bundle: self.bundleName,
              _authenticator: utils.getAuthenticator()
            }),
            success: function(data){
              self.rview.options.data.overrides.push(data.filepath);
              self.rview.tabView.overridesView.render();
              self.addResult(_t('finished saving css bundles'));
              self.finished();
            },
            error: function(){
              self.addResult(_t('Error saving css bundle'));
              self.finished(true);
            }
          });
        }else if($styles.length === config.less.length){
          $styles.each(function(){$(this).remove();});
          /* XXX is this dead code? */
          script = document.createElement('script');
          script.setAttribute('type', 'text/javascript');
          script.setAttribute('src', self.rview.options.data.lessModifyUrl);
          head.appendChild(script);

          lessModified = true;
          setTimeout(checkFinished, 300);
        }else{
          setTimeout(checkFinished, 300);
        }
      };
      checkFinished();
    };

    self.buildCSSBundle = function(){
      self.addResult(_t('building CSS bundle'));
      $.ajax({
        url: self.rview.options.data.manageUrl,
        type: 'POST',
        dataType: 'json',
        data: {
          action: 'less-build-config',
          bundle: self.bundleName,
          _authenticator: utils.getAuthenticator()
        },
        success: function(data){
          /* sort of weird here, follow along. We'll build CSS after JS */
          self._buildCSSBundle(data);
        },
        error: function(){
          self.addResult(_t('Error building css bundle'));
          self.finished(true);
        }
      });
    };

    self._buildJSBundle = function(config){
      if(config.include.length === 0){
        self.addResult(_t('No javascripts to build, skipping'));
        return self.buildCSSBundle();
      }

      config.out = function(results){
        $.ajax({
          url: self.rview.options.data.manageUrl,
          type: 'POST',
          dataType: 'json',
          data: {
            action: 'save-js-build',
            bundle: self.bundleName,
            data: results,
            _authenticator: utils.getAuthenticator()
          },
          success: function(data){
            self.rview.options.data.overrides.push(data.filepath);
            self.rview.tabView.overridesView.render();
          },
          error: function(){
            self.addResult(_t('Error building bundle'));
            self.finished(true);
          }
        });
      };
      new IFrame({
        name: 'rjs',
        resources: [self.rview.options.data.rjsUrl],
        onLoad: function(iframe){
          iframe.window.requirejs.optimize(config, function(combined_files){
            self.addResult(_t('Saved javascript bundle, Build results') + ': <pre>' + combined_files + '</pre>');
            self.buildCSSBundle();
            iframe.destroy();
          });
        }
      });
    };

    return self;
  };

  return Builder;
});
