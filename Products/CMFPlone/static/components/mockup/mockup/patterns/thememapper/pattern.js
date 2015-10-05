/* Theme Mapper pattern.
 *
 * Options:
 *    filemanagerConfig(object): The file manager pattern config ({})
 *    mockupUrl(string): Mockup url (null)
 *    unthemedUrl(string): unthemed site url (null)
 *    helpUrl(string): Helper docs url (null)
 *    previewUrl(string): url to preview theme (null)
 *
 *
 * Documentation:
 *
 *    # Basic example
 *
 *    {{ example-1 }}
 *
 *
 * Example: example-1
 *
 *    <div class="pat-thememapper"
 *         data-pat-thememapper='filemanagerConfig:{"actionUrl":"/filemanager-actions"};
 *                               mockupUrl:/tests/files/mapper.html;
 *                               unthemedUrl:/tests/files/mapper.html;
 *                               previewUrl:http://www.google.com;
 *                               helpUrl:http://docs.diazo.org/en/latest'></div>
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'underscore',
  'translate',
  'text!mockup-patterns-thememapper-url/templates/inspector.xml',
  'mockup-patterns-filemanager',
  'mockup-patterns-thememapper-url/js/rulebuilder',
  'mockup-patterns-thememapper-url/js/rulebuilderview',
  'mockup-patterns-thememapper-url/js/lessbuilderview',
  'mockup-patterns-thememapper-url/js/cacheview',
  'mockup-ui-url/views/button',
  'mockup-ui-url/views/buttongroup',
  'mockup-utils'
], function($, Base, _, _t, InspectorTemplate, FileManager, RuleBuilder, RuleBuilderView, LessBuilderView, CacheView, ButtonView, ButtonGroup, utils) {
  'use strict';

  var inspectorTemplate = _.template(InspectorTemplate);

  var Inspector = Base.extend({
    defaults: {
      name: 'name',
      ruleBuilder: null,
      showReload: false
    },
    init: function() {
      var self = this;
      self.enabled = true;
      self.currentOutline = null;
      self.activeClass = '_theming-highlighted';
      self.saved = null;
      self.ruleBuilder = self.options.ruleBuilder;

      self.$el.html(inspectorTemplate(self.options));
      self.$on = $('.turnon', self.$el);
      self.$off = $('.turnoff', self.$el);
      self.$frame = $('iframe', self.$el);
      self.$frameInfo = $('.frame-info', self.$el);
      self.$frameShelfContainer = $('.frame-shelf-container', self.$el);
      self.$selectorInfo = $('.selector-info', self.$frameShelfContainer);
      self.$currentSelector = $('.current-selector', self.$frameInfo);

      self.$reloadBtn = $('a.refresh', self.$el);

      $('a.clearInspector', self.$frameShelfContainer).click(function(e) {
        e.preventDefault();
        self.save(null);
      });
      self.$reloadBtn.click(function(e) {
        e.preventDefault();
        self.$frame.attr('src', self.$frame.attr('src'));
        self.setupFrame();
      });
      $('a.fullscreen', self.$el).click(function(e){
        e.preventDefault();
        if (self.$el.hasClass('show-fullscreen')){
          self.$el.removeClass('show-fullscreen');
        } else {
          self.$el.addClass('show-fullscreen');
        }
      });

      if (!self.options.showReload){
        self.$reloadBtn.hide();
      }

      self.$on.click(function() {
        self.on();
      });
      self.$off.click(function() {
        self.off();
      });

      self.setupFrame();
    },
    on: function() {
      var self = this;
      self.$off.prop('disabled', false);
      self.$on.prop('disabled', true);
      self.enabled = true;
    },
    off: function() {
      var self = this;
      self.$on.prop('disabled', false);
      self.$off.prop('disabled', true);
      self.enabled = false;
    },
    setupFrame: function() {
      var self = this;
      /* messy way to check if iframe is loaded */
      var checkit = function() {
        if (self.$frame.contents().find('body').find('*').length > 0){
          self._setupFrame();
        } else {
          setTimeout(checkit, 100);
        }
      };
      setTimeout(checkit, 200);
    },
    _setupFrame: function() {
      var self = this;

      self.$frame.contents().find('*').hover(function(e) {
        if(self.enabled) {
          e.stopPropagation();
          self.$frame.focus();
          self.setOutline(this);
        }
      }, function() {
        if($(this).hasClass(self.activeClass)) {
          self.clearOutline(this);
        }
      }).click(function (e) {
        if(self.enabled) {
          e.stopPropagation();
          e.preventDefault();

          self.setOutline(this);
          self.save(this);
          return false;
        }
        return true;
      });

      self.$frame.contents().keyup(function(e) {
        if (!self.enabled){
          return true;
        }

        // ESC -> Move selection to parent node
        if(e.keyCode === 27 && self.currentOutline !== null) {
          e.stopPropagation();
          e.preventDefault();

          var parent = self.currentOutline.parentNode;
          if(parent !== null && parent.tagName !== undefined) {
            self.setOutline(parent);
          }
        }

        // Enter -> Equivalent to clicking on selected node
        if(e.keyCode === 13 && self.currentOutline !== null) {
          e.stopPropagation();
          e.preventDefault();

          self.save(self.currentOutline);

          return false;
        }
      });
    },
    save: function(element) {
      var self = this;
      this.saved = element;
      if(element === null) {
        self.$frameShelfContainer.hide();
      } else {
        self.$frameShelfContainer.show();
      }

      self.animateSelector();
      self.$selectorInfo.text(element === null ? '' : self.ruleBuilder.bestSelector(element));

      self.onsave(this, element);
    },
    clearOutline: function(element){
      var self = this;
      $(element).css('outline', '');
      $(element).css('cursor', '');

      $(element).removeClass(self.activeClass);

      self.currentOutline = null;
      self.$currentSelector.text('');
      self.onselect(self, null);
    },
    setOutline: function(element) {
      var self = this;
      var $el = $(element);

      $el.css('outline', 'solid red 1px');
      $el.css('cursor', 'crosshair');

      $el.addClass(self.activeClass);

      if(self.currentOutline !== null) {
        self.clearOutline(self.currentOutline);
      }
      self.currentOutline = element;
      self.$currentSelector.text(self.ruleBuilder.bestSelector(element));

      self.onselect(self, element);
    },
    animateSelector: function(highlightColor, duration) {
      var self = this;
      var highlightBg = highlightColor || '#FFFFE3';
      var animateMs = duration || 750;
      var originalBg = self.$frameInfo.css('background-color');

      if (!originalBg || originalBg === highlightBg){
          originalBg = '#FFFFFF'; // default to white
      }

      self.$frameInfo
        .css('backgroundColor', highlightBg)
        .animate({ backgroundColor: originalBg }, animateMs, null, function () {
          self.$frameInfo.css('backgroundColor', originalBg);
        });
    },
    onsave: function(highlighter, node) {
      var self = this;
      if(node == null) {
        self.$el.find('.frame-shelf-container').hide();
      } else {
        self.$el.find('.frame-shelf-container').show();
      }

      self.animateSelector(self.$el.find('.frame-info'));
      self.$el.find('.selector-info').text(node == null? "" : self.ruleBuilder.bestSelector(node));

      if(self.ruleBuilder.active) {
        self.ruleBuilder.select(node);
        self.ruleBuilder.next();
      }

    },
    onselect: function(highlighter, node) {
      var self = this;
      self.$currentSelector.text(node == null? "" : self.ruleBuilder.bestSelector(node));
    }
  });


  var ThemeMapper = Base.extend({
    name: 'thememapper',
    trigger: '.pat-thememapper',
    defaults: {
      filemanagerConfig: {},
      themeUrl: null,
      mockupUrl: null,
      unthemedUrl: null,
      helpUrl: null,
      previewUrl: null,
      editable: false
    },
    buttonGroup: null,
    showInspectorsButton: null,
    buildRuleButton: null,
    previewThemeButton: null,
    helpButton: null,
    hidden: true,
    fileManager: null,
    mockupInspector: null,
    unthemedInspector: null,
    ruleBuilder: null,
    rulebuilderView: null,
    devPath: null,
    prodPath: null,
    lessUrl: null,
    lessPaths: {},
    lessVariableUrl: null,
    $fileManager: null,
    $container: null,
    $inspectorContainer: null,
    $mockupInspector: null,
    $unthemedInspector: null,
    init: function() {
      var self = this;
      if(typeof(self.options.filemanagerConfig) === 'string'){
        self.options.filemanagerConfig = $.parseJSON(self.options.filemanagerConfig);
      }
      self.$fileManager = $('<div class="pat-filemanager"/>').appendTo(self.$el);
      self.$container = $('<div class="row"></div>').appendTo(self.$el);
      self.$styleBox = $('<div id="styleBox"></div>').appendTo(self.$el);
      self.$inspectorContainer = $('<div id="inspectors"></div>').appendTo(self.$container);
      self.$mockupInspector = $('<div class="mockup-inspector"/>').appendTo(self.$inspectorContainer);
      self.$unthemedInspector = $('<div class="unthemed-inspector"/>').appendTo(self.$inspectorContainer);

      // initialize patterns now
      self.editable = (self.options.editable == "True") ? true : false;
      self.lessUrl = (self.options.lessUrl !== undefined ) ? self.options.lessUrl : false;
      self.lessVariableUrl = (self.options.lessVariables !== undefined ) ? self.options.lessVariables : false;

      self.devPath = [];
      self.prodPath = [];

      self.options.filemanagerConfig.uploadUrl = self.options.themeUrl;
      self.options.filemanagerConfig.theme = true;
      self.fileManager = new FileManager(self.$fileManager, self.options.filemanagerConfig);
      self.fileManager.setUploadUrl();

      self.setupButtons();

      self.ruleBuilder = new RuleBuilder(self, self.ruleBuilderCallback);

      self.fileManager.on("fileChange", function() {
        var node = self.fileManager.getSelectedNode();
        self.setLessPaths(node);
      });

      self.mockupInspector = new Inspector(self.$mockupInspector, {
        name: _t('HTML mockup'),
        ruleBuilder: self.ruleBuilder,
        url: self.options.mockupUrl,
        showReload: true,
      });
      self.unthemedInspector = new Inspector(self.$unthemedInspector, {
        name: _t('Unthemed content'),
        ruleBuilder: self.ruleBuilder,
        url: self.options.unthemedUrl,
      });
      self.fileManager.$tree.bind('tree.click', function(e){
      });
      self.buildLessButton.disable();

      if( !self.editable ) {
        if( self.fileManager.toolbar ) {
          var items = self.fileManager.toolbar.items;
          $(items).each(function() {
            this.disable();
          });
          self.lessbuilderView.triggerView.disable();
        }
      };

      // initially, let's hide the panels
      self.hideInspectors();
      self.getManifest();
    },
    getManifest: function() {
      var self = this;

      self.fileManager.doAction('getFile', {
        datatype: 'json',
        data: {
          path: 'manifest.cfg'
        },
        success: function(data) { this.setDefaultPaths(data); }.bind(self)
      })
    },
    setSavePath: function() {
        var self = this;
        var filename = self.lessbuilderView.$filename.val()

        if( filename == "" ) {
            filename = self.lessbuilderView.$filename.attr('placeholder');
        }

        var s = self.lessPaths['save'];
        var folder = s.substr(0, s.lastIndexOf('/'));

        var savePath = folder + '/' + filename;
        self.lessPaths['save'] = savePath;
    },
    setLessPaths: function(node) {
      var self = this;

      if( node.fileType == "less" ){
        self.buildLessButton.enable();
      }
      else{
        self.buildLessButton.disable();
      }

      if( node.path != "" ) {
        var reg = new RegExp("/(.*\\.)less$", "m");
        var path = reg.exec(node.path);

        if( path === null ) {
          self.lessPaths = {};
          return false;
        }
        var lessPath = path[1] + "less";
        var cssPath = path[1] + "css";

        //file paths should be in the form of:
        // "[directory/]filename.less"
        self.lessPaths = {
          'less': lessPath,
          'save': cssPath
        };

        return true;
      }
      else {
        self.lessPaths = {};
        return false;
      }
    },
    setDefaultPaths: function(manifest) {
      var self = this;
      var dev = new RegExp("development-css\\s*=\\s*\\/\\+\\+theme\\+\\+.*?\\/(.*)");
      var prod = new RegExp("production-css\\s*=\\s*\\/\\+\\+theme\\+\\+.*?\\/(.*)");

      var devUrl = dev.exec(manifest.contents)[1];
      var prodUrl = prod.exec(manifest.contents)[1];

      //The array lets us get around scoping issues.
      self.devPath[0] = devUrl;
      self.prodPath[0] = prodUrl;
    },
    saveThemeCSS: function(styles) {
      var self = this.env;

      if( styles === "" || styles === undefined ) {
        //There was probably a problem during compilation
        return false;
      }

      self.setSavePath();

      self.fileManager.doAction('saveFile', {
        type: 'POST',
        data: {
          path: self.lessPaths['save'],
          relativeUrls: true,
          data: styles,
          _authenticator: utils.getAuthenticator()
        },
        success: function(data) {
          self.fileManager.refreshTree(function() {
            //We need to make sure we open the newest version
            delete self.fileManager.fileData['/' + self.lessPaths['save']]
            self.fileManager.selectItem(self.lessPaths['save'])
          });
          self.lessbuilderView.end();
        }
      });

      window.iframe['lessc'].destroy();

    },
    showInspectors: function(){
      var self = this;
      var $parent = self.$mockupInspector.parent();
      $parent.slideDown();
      self.hidden = false;
      self.showInspectorsButton.options.title = 'Hide inspectors';
      self.showInspectorsButton.applyTemplate();
      $('html, body').animate({
        scrollTop: $parent.offset().top - 50
      }, 500);
    },
    hideInspectors: function(){
      var self = this;
      var $parent = self.$mockupInspector.parent();
      $parent.slideUp();
      self.hidden = true;
      self.showInspectorsButton.options.title = 'Show inspectors';
      self.showInspectorsButton.applyTemplate();
    },
    setupButtons: function(){
      var self = this;
      self.showInspectorsButton = new ButtonView({
        id: 'showinspectors',
        title: _t('Show inspectors'),
        icon: 'search',
        tooltip: _t('Show inspector panels'),
        context: 'default'
      });
      self.showInspectorsButton.on('button:click', function(){
        if (self.hidden) {
          self.showInspectors();
        } else {
          self.hideInspectors();
        }
      });

      self.buildRuleButton = new ButtonView({
        id: 'buildrule',
        title: _t('Build rule'),
        icon: 'wrench',
        tooltip: _t('rule building wizard'),
        context: 'default'
      });
      self.fullscreenButton = new ButtonView({
        id: 'fullscreenEditor',
        title: _t('Fullscreen'),
        icon: 'fullscreen',
        tooltip: _t('view the editor in fullscreen'),
        context: 'default'
      });
      self.fullscreenButton.on('button:click', function() {
        var btn = $('<a href="#">'+
            '<span class="btn btn-danger closeeditor">' + _t("Close Fullscreen") + '</span>'+
            '</a>').prependTo($('.tree'));

        $(btn).click(function() {
          $('.container').removeClass('fullscreen').trigger('resize');
          $(btn).remove();
        });
        //resize tells the editor window to resize as well.
        $('.container').addClass('fullscreen').trigger('resize');
      });
      self.previewThemeButton = new ButtonView({
        id: 'previewtheme',
        title: _t('Preview theme'),
        icon: 'new-window',
        tooltip: _t('preview theme in a new window'),
        context: 'default'
      });
      self.previewThemeButton.on('button:click', function(){
        window.open(self.options.previewUrl);
      });
      self.buildLessButton = new ButtonView({
        id: 'buildless',
        title: _t('Build CSS'),
        icon: 'cog',
        tooltip: _t('Compile LESS file'),
        context: 'default'
      });
      self.refreshButton = new ButtonView({
        id: 'refreshButton ',
        title: _t('Refresh'),
        icon: 'refresh',
        tooltip: _t('Reload the current file'),
        context: 'default'
      });
      self.refreshButton.on("button:click", function() {
        self.fileManager.refreshFile();
      });
      self.cacheButton = new ButtonView({
        id: 'cachebutton',
        title: _t('Clear cache'),
        icon: 'floppy-remove',
        tooltip: _t('Clear site\'s theme cache'),
        context: 'default'
      });
      self.helpButton = new ButtonView({
        id: 'helpbutton',
        title: _t('Help'),
        icon: 'question-sign',
        tooltip: _t('Show help'),
        context: 'default'
      });
      self.helpButton.on('button:click', function(){
        window.open(self.options.helpUrl);
      });
      self.rulebuilderView = new RuleBuilderView({
        triggerView: self.buildRuleButton,
        app: self
      });
      self.cacheView = new CacheView({
        triggerView: self.cacheButton,
        app: self
      })
      self.lessbuilderView = new LessBuilderView({
        triggerView: self.buildLessButton,
        app: self
      });
      self.buttonGroup = new ButtonGroup({
        items: [
          self.showInspectorsButton,
          self.buildRuleButton,
          self.previewThemeButton,
          self.fullscreenButton,
          self.buildLessButton,
          self.refreshButton,
          self.cacheButton,
          self.helpButton
        ],
        id: 'mapper'
      });
      $('#toolbar .navbar', self.$el).append(self.buttonGroup.render().el);
      $('#toolbar .navbar', self.$el).append(self.rulebuilderView.render().el);
      $('#toolbar .navbar', self.$el).append(self.cacheView.render().el);
      $('#toolbar .navbar', self.$el).append(self.lessbuilderView.render().el);
    }
  });

  return ThemeMapper;

});
