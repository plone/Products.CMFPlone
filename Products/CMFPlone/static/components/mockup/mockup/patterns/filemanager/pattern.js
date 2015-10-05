/* Filemanager pattern.
 *
 * Options:
 *    aceConfig(object): ace configuration ({})
 *    actionUrl(string): base url to get/put data. Action is passed is an a parameters, ?action=(dataTree, newFile, deleteFile, getFile, saveFile)
 *    uploadUrl(string): url to upload files to
 *    resourceSearchUrl(string): url to search for resources to customize
 *
 * Documentation:
 *
 *
 *   {{ example-1 }}
 *
 *   Example with upload
 *
 *   {{ example-2 }}
 *
 * Example: example-1
 *    <div class="pat-filemanager"
 *         data-pat-filemanager="actionUrl:/filemanager-actions;
 *                               resourceSearchUrl:/search-resources;">
 *    </div>
 *
 * Example: example-2
 *    <div class="pat-filemanager"
 *         data-pat-filemanager="actionUrl:/filemanager-actions;
 *                               uploadUrl:/upload;
 *                               resourceSearchUrl:/search-resources;">
 *    </div>
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'underscore',
  'backbone',
  'mockup-ui-url/views/base',
  'mockup-patterns-tree',
  'mockup-patterns-texteditor',
  'text!mockup-patterns-filemanager-url/templates/app.xml',
  'mockup-ui-url/views/toolbar',
  'mockup-ui-url/views/button',
  'mockup-ui-url/views/buttongroup',
  'mockup-patterns-filemanager-url/js/addnew',
  'mockup-patterns-filemanager-url/js/newfolder',
  'mockup-patterns-filemanager-url/js/delete',
  'mockup-patterns-filemanager-url/js/customize',
  'mockup-patterns-filemanager-url/js/rename',
  'mockup-patterns-filemanager-url/js/upload',
  'translate',
  'mockup-utils',
  'text!mockup-ui-url/templates/popover.xml'
], function($, Base, _, Backbone, BaseView, Tree, TextEditor, AppTemplate, Toolbar,
            ButtonView, ButtonGroup, AddNewView, NewFolderView, DeleteView,
            CustomizeView, RenameView, UploadView, _t, utils) {
  'use strict';

  var FileManager = Base.extend({
    name: 'filemanager',
    trigger: '.pat-filemanager',
    template: _.template(AppTemplate),
    tabItemTemplate: _.template(
      '<li class="active" data-path="<%= path %>">' +
        '<a href="#" class="select"><%= path %></a>' +
        '<a href="#" class="remove">' +
          '<span class="glyphicon glyphicon-remove-circle"></span>' +
        '</a>' +
      '</li>'),
    saveBtn: null,
    uploadFolder: '',
    fileData: {},  /* mapping of files to data that it describes */
    defaults: {
      aceConfig: {},
      actionUrl: null,
      uploadUrl: null,
      resourceSearchUrl: null,
      treeConfig: {
        autoOpen: true
      }
    },
    init: function() {
      var self = this;

      if (self.options.actionUrl === null) {
        self.$el.html('Must specify actionUrl setting for pattern');
        return;
      }

      self.options.treeConfig = $.extend(true, {}, self.treeConfig, {
        dataUrl: self.options.actionUrl + '?action=dataTree',
        onCreateLi: function(node, li) {
          var imageTypes = ['png', 'jpg', 'jpeg', 'gif', 'ico'];
          var themeTypes = ['css', 'html', 'htm', 'txt', 'xml', 'js', 'cfg', 'less'];

          $('span', li).addClass('glyphicon');
          if( node.folder ) {
            $('span', li).addClass('glyphicon-folder-close')
          }
          else if( $.inArray(node.fileType, imageTypes) >= 0) {
            $('span', li).addClass('glyphicon-picture');
          }
          else if( $.inArray(node.fileType, themeTypes) >= 0) {
            $('span', li).addClass('glyphicon-file');
          }
          else {
            $('span', li).addClass('glyphicon-cog')
          }
        }
      });

      self.fileData = {};

      self.saveBtn = new ButtonView({
        id: 'save',
        title: _t('Save'),
        icon: 'floppy-disk',
        context: 'primary'
      });

      var newFolderView = new NewFolderView({
        triggerView: new ButtonView({
          id: 'newfolder',
          title: _t('New folder'),
          tooltip: _t('Add new folder to current directory'),
          icon: 'folder-open',
          context: 'default'
        }),
        app: self
      });
      var addNewView = new AddNewView({
        triggerView: new ButtonView({
          id: 'addnew',
          title: _t('Add new file'),
          tooltip: _t('Add new file to current folder'),
          icon: 'file',
          context: 'default'
        }),
        app: self
      });
      var renameView = new RenameView({
        triggerView: new ButtonView({
          id: 'rename',
          title: _t('Rename'),
          tooltip: _t('Rename currently selected resource'),
          icon: 'random',
          context: 'default'
        }),
        app: self
      });
      var deleteView = new DeleteView({
        triggerView: new ButtonView({
          id: 'delete',
          title: _t('Delete'),
          tooltip: _t('Delete currently selected resource'),
          icon: 'trash',
          context: 'danger'
        }),
        app: self
      });

      self.views = [
        newFolderView,
        addNewView,
        renameView,
        deleteView
      ];
      var mainButtons = [
        self.saveBtn,
        newFolderView.triggerView,
        addNewView.triggerView,
        renameView.triggerView,
        deleteView.triggerView
      ];

      if (self.options.uploadUrl && utils.featureSupport.dragAndDrop() && utils.featureSupport.fileApi()){
        var uploadView = new UploadView({
          triggerView: new ButtonView({
            id: 'upload',
            title: _t('Upload'),
            tooltip: _t('Upload file to current directory'),
            icon: 'upload',
            context: 'default'
          }),
          app: self,
          callback: function(data) {
            var path = self.uploadFolder + '/' + data.name;
            self.refreshTree(function() {
              self.selectItem(path);
              self.getUpload().toggle();
            });

          }
        });
        self.views.push(uploadView);
        mainButtons.push(uploadView.triggerView);
      }
      if (self.options.resourceSearchUrl){
        var customizeView = new CustomizeView({
          triggerView: new ButtonView({
            id: 'customize',
            title: _t('Add new override'),
            tooltip: _t('Find resource in plone to override'),
            context: 'default'
          }),
          app: self
        });
        self.views.push(customizeView);
        mainButtons.push(customizeView.triggerView);
      }

      self.toolbar = new Toolbar({
        items: [
          new ButtonGroup({
            items: mainButtons,
            id: 'main',
            app: self
          })
        ]
      });

      self._save = function() {

        var path = $('.active', self.$tabs).data('path');
        if( path === undefined || path === false ) {
          alert("No file selected.");
          return;
        }
        self.doAction('saveFile', {
          type: 'POST',
          data: {
            path: path,
            data: self.ace.editor.getValue(),
            _authenticator: utils.getAuthenticator()
          },
          success: function(data) {
            if( data['error'] !== undefined ) {
              alert("There was a problem saving the file.");
            }
            $('[data-path="' + path + '"]').removeClass("modified");
          }
        });
      };

      self.saveBtn.on('button:click', function() {
        self._save();
      });
      self.render();
    },
    $: function(selector){
      return this.$el.find(selector);
    },
    refreshTree: function(callback) {
      var self = this;
      if( callback === undefined ) {
        callback = function() {};
      }
      self.$tree.tree('loadDataFromUrl',
        self.options.actionUrl + '?action=dataTree',
        null,
        callback
      );
    },
    render: function(){
      var self = this;
      self.$el.html(self.template(self.options));
      self.$('#toolbar').append(self.toolbar.render().el);
      _.each(self.views, function(view) {
        self.$('#toolbar').append(view.render().el);
      });
      self.$tree = self.$('.tree');
      self.$nav = self.$('nav');
      self.$tabs = $('ul.nav', self.$nav);
      self.tree = new Tree(self.$tree, self.options.treeConfig);
      self.$editor = self.$('.editor');

      /* close popovers when clicking away */
      $(document).click(function(e){
          var $el = $(e.target);
          if(!$el.is(':visible')){
              // ignore this, fake event trigger to element that is not visible
              return;
          }
          if($el.is('a') || $el.parent().is('a')){
              return;
          }
          var $popover = $('.popover:visible');
          if($popover.length > 0 && !$.contains($popover[0], $el[0])){
              var popover = $popover.data('component');
              if(popover){
                  popover.hide();
              }
          }
      });

      self.$tree.bind('tree.select', function(e) {
        if( e.node === null ) {
          self.toggleButtons(false);
        }
        else{
          self.toggleButtons(true);
          self.handleClick(e);
        }
      });

      self.$tree.bind('tree.open', function(e) {
        var element = $(e.node.element).find(':first').find('.glyphicon');
        $(element).addClass('glyphicon-folder-open');
        $(element).removeClass('glyphicon-folder-close');
      });

      self.$tree.bind('tree.close', function(e) {
        var element = $(e.node.element).find(':first').find('.glyphicon');
        $(element).addClass('glyphicon-folder-close');
        $(element).removeClass('glyphicon-folder-open');
      });

      self.$tree.bind('tree.init', function(e) {
        var node = self.$tree.tree('getTree').children[0];
        if( node ) {
          self.$tree.tree('selectNode', node);
        }
      });

      $(self.$tabs).on('click', function(e) {
        var path = $(e.target).data('path');
        if( path === undefined ) {
          path = $(e.target.parentElement).data('path');
          if( path === undefined ) {
            return false;
          }
        }
        self.selectItem(path);
      });
      $(window).on('resize', function() {
        self.resizeEditor();
      });
    },
    toggleButtons: function(on) {
      if( on === undefined ) {
        return;
      }

      if( on ) {
        $('#btn-delete', this.$el).attr('disabled', false);
        $('#btn-save', this.$el).attr('disabled', false);
        $('#btn-rename', this.$el).attr('disabled', false);
      }
      else{
        $('#btn-delete', this.$el).attr('disabled', 'disabled');
        $('#btn-save', this.$el).attr('disabled', 'disabled');
        $('#btn-rename', this.$el).attr('disabled', 'disabled');
      }
    },
    handleClick: function(event) {
      var self = this;
      self.closeActivePopovers();
      self.openFile(event);
    },
    closeActiveTab: function() {
      var self = this;
      var active = self.$tabs.find('.active .remove');
      var $siblings = $(active).parent().siblings();
      if ($siblings.length > 0){
        var $item;
        if ($(active).parent().prev().length > 0){
          $item = $(active).parent().prev();
        } else {
          $item = $(active).parent().next();
        }
        $(active).parent().remove();
        $item.click();
      } else {
        $(active).parent().remove();
        self.toggleButtons(false);
        self.openEditor();
      }
    },
    closeTab: function(path) {
      var self = this;
      if( path === undefined ) {
        return;
      }

      var tabs = self.$tabs.children();

      $(tabs).each(function() {
        if( $(this).data('path') == path )
        {
          $(this).find('a.remove').trigger('click');
        }
      });
    },
    closeActivePopovers: function() {
      var self = this;
      var active = $('.navbar a.active');
      $(active).each(function() {
        $(this).click();
      });
    },
    createTab: function(path) {
      var self = this;
      var $item = $(self.tabItemTemplate({path: path}));
      self.shrinkTab($item);
      self.$tabs.append($item);
      $('.remove', $item).click(function(e){
        e.preventDefault();
        e.stopPropagation();
        self.closeActivePopovers();
        if ($(this).parent().hasClass('active'))
        {
          self.closeActiveTab();
        }
        else {
          $(this).parent().remove();
        }
      });
      $('.select', $item).click(function(e){
        e.preventDefault();
        $('li', self.$tabs).removeClass('active');
        var $li = $(this).parent();
        self.closeActivePopovers();
        $li.addClass('active');
      });
    },
    updateTabs: function(path) {
      var self = this;
      if( path === undefined ) {
        return;
      }
      $('li', self.$tabs).removeClass('active');
      var $existing = $('[data-path="' + path + '"]', self.$tabs);
      if ($existing.length === 0){
        self.createTab(path);
      }else{
        $existing.addClass('active');
      }
    },
    shrinkTab: function(tab) {
        var self = this;
        if( self.$tabs.hasClass('smallTabs') ) {
            tab = $(tab);
            var text = tab.text();
            if( text.lastIndexOf('/') > 0 )
            {
                text = text.substr(text.lastIndexOf('/') + 1);
                tab.find('.select').text(text);
            }
        }
    },
    openFile: function(event) {
      var self = this;
      if( event.node === null ) {
        return true;
      }
      if (event.node.folder){
        if( self.options.theme ) {
          self.setUploadUrl(event.node.path);
        }
        return true;
      }
      var doc = event.node.path;
      if(self.fileData[doc]) {
        self.openEditor(doc);

        var resetLine = function() {
          if( self.fileData[doc].line === undefined ) {
            return;
          }
          self.ace.editor.scrollToLine(self.fileData[doc].line);
          self.ace.editor.moveCursorToPosition(self.fileData[doc].cursorPosition)
          //We only want this to fire after the intial render,
          //Not after rendering a "scroll" or "focus" event,
          //So we remove it immediately after.
          self.ace.editor.renderer.off("afterRender", resetLine);
        };
        //This sets the listener before rendering finishes
        self.ace.editor.renderer.on("afterRender", resetLine);
      } else {
        self.doAction('getFile', {
          data: { path: doc },
          dataType: 'json',
          success: function(data) {
            self.fileData[doc] = data;
            self.openEditor(doc);
          }
        });
      }
    },
    getNodeByPath: function(path) {
      var self = this;
      if( path === undefined || path === "" )
      {
       return null;
      }

      if( path.indexOf('/') === 0 )
      {
        path = path.substr(1,path.length);
      }

      var folders = path.split('/');
      var children = self.$tree.tree('getTree').children;

      for( var i = 0; i < folders.length; i++ )
      {
        for( var z = 0; z < children.length; z++ )
        {
          if( children[z].name == folders[i] ) {
            if( children[z].folder == true && i != (folders.length - 1) ) {
              children = children[z].children;
              break;
            }
            else {
              return children[z];
            }
          }
        }
      }

      return null;
    },
    doAction: function(action, options) {
      var self = this;
      if (!options){
        options = {};
      }
      $.ajax({
        url: self.options.actionUrl,
        type: options.type || 'GET',
        data: $.extend({}, {
          _authenticator: utils.getAuthenticator(),
          action: action
        }, options.data || {}),
        success: options.success,
        failure: options.failure || function() {}
      });
    },
    openEditor: function(path) {
      var self = this;

      if( path !== undefined ) {
          self.updateTabs(path);
      }

      // first we need to save the current editor content
      if(self.currentPath) {
        self.fileData[self.currentPath].contents = self.ace.editor.getValue();
        var lineNum = self.ace.editor.getFirstVisibleRow();
        self.fileData[self.currentPath].line = lineNum;
        self.fileData[self.currentPath].cursorPosition = self.ace.editor.getCursorPosition();
      }
      self.currentPath = path;
      if (self.ace !== undefined){
        self.ace.editor.destroy();
        self.ace.editor.container.parentNode.replaceChild(
          self.ace.editor.container.cloneNode(true),
          self.ace.editor.container
        );
      }
      self.ace = new TextEditor(self.$editor);

      if( self.currentPath === undefined ) {
          self.ace.setText();
          self.ace.setSyntax('text');
          self.ace.editor.clearSelection();
          self.$tree.tree('selectNode', null);
      }
      else if( typeof self.fileData[path].info !== 'undefined' )
      {
          var preview = self.fileData[path].info;
          if( self.ace.editor !== undefined ) {
              self.ace.editor.off();
          }
          $('.ace_editor').empty().append(preview);
      }
      else
      {
          self.ace.setText(self.fileData[path].contents);
          self.ace.setSyntax(path);
          self.ace.editor.clearSelection();
      }

      self.resizeEditor();
      self.$el.trigger("fileChange");
      self.ace.editor.on('change', function() {
        if (self.ace.editor.curOp && self.ace.editor.curOp.command.name) {
          $('[data-path="' + path + '"]').addClass("modified");
        }
      });
      self.ace.editor.on('paste', function() {
        $('[data-path="' + path + '"]').addClass("modified");
      });
      self.ace.editor.commands.addCommand({
        name: 'saveFile',
        bindKey: {
          win: 'Ctrl-S', mac: 'Command-S',
          sender: 'editor|cli'
        },
        exec: function (env, args, request) {
          self._save();
        }
      });
    },
    getSelectedNode: function() {
      return this.$tree.tree('getSelectedNode');
    },
    getNodePath: function(node) {
      var self = this;
      if(node === undefined){
        node = self.getSelectedNode();
      }
      var path = self.getFolderPath(node.parent);
      if (path !== '/'){
        path += '/';
      }

      var name = (node.name !== undefined) ? node.name : '';
      return path + name;
    },
    getFolderPath: function(node){
      var self = this;
      if(node === undefined){
        node = self.getSelectedNode();
      }
      var parts = [];
      if (!node.folder && node.name){
        node = node.parent;
      }
      while (node.name){
        parts.push(node.name);
        node = node.parent;
      }
      parts.reverse();
      return '/' + parts.join('/');
    },
    getUpload: function() {
      var self = this;

      return _.find(self.views, function(x) { return x.upload !== undefined });
    },
    resizeEditor: function() {
        var self = this;

        self.$editor = $('.editor', self.$el);
        var tab = self.$tabs.children()[0];
        if( $(tab).outerHeight() < (self.$tabs.height() - 1) ) {
            self.$tabs.addClass('smallTabs');
            $(self.$tabs.children()).each(function() {
                self.shrinkTab(this);
            });
        }
        var tabBox = self.$tabs.parent();

        //Contains both the tabs, and editor window
        var container = tabBox.parent().parent();
        var h = container.innerHeight();
        h -= tabBox.outerHeight();

        //+2 for the editor borders
        h -= 2;
        //accounts for the borders/margin
        self.$editor.height(h);
        var w = container.innerWidth();
        w -= (container.outerWidth(true) - container.innerWidth());

        self.$editor.width(w);
        if (self.ace !== undefined){
          //This forces ace to redraw if the container has changed size
          self.ace.editor.resize();
          self.ace.editor.$blockScrolling = Infinity;
          self.ace.editor.focus();
        }
    },
    selectItem: function(path) {
      var self = this;
      var node = self.getNodeByPath(path);
      self.$tree.tree('selectNode', node);
    },
    setUploadUrl: function(path) {
      var self = this;

      if( path === undefined ) {
        path = "";
      }

      self.uploadFolder = path;
      var view = self.getUpload();
      if( view !== undefined ) {
        var url = self.options.uploadUrl +
                  path +
                  "/themeFileUpload" +
                  "?_authenticator=" +
                  utils.getAuthenticator();

        view.upload.dropzone.options.url = url;
      }
    },
    refreshFile: function(path) {
      var self = this;

      if( path === undefined ) {
        path = self.getSelectedNode().path;
      }
      self.closeTab(path);
      delete self.fileData[path];
      self.selectItem(path);
    }
  });

  return FileManager;

});
