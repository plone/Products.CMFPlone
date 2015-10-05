/* Upload pattern.
 *
 * Options:
 *    showTitle(boolean): show/hide the h1 title (true)
 *    url(string): If not used with a form, this option must provide the URL to submit to or baseUrl with relativePath needs to be used (null)
 *    baseUrl(string): to be used in conjunction with relativePath to generate submission urls based on related items (null)
 *    relativePath(string): again, to be used with baseUrl to create upload url (null)
 *    initialFolder(string): UID of initial folder related items widget should have selected (null)
 *    currentPath(string): Current path related items is starting with (null)
 *    className(string): value for class attribute in the form element ('upload')
 *    paramName(string): value for name attribute in the file input element ('file')
 *    ajaxUpload(boolean): true or false for letting the widget upload the files via ajax. If false the form will act like a normal form. (true)
 *    wrap(boolean): true or false for wrapping this element using the value of wrapperTemplate. (false)
 *    wrapperTemplate(string): HTML template for wrapping around with this element. ('<div class="upload-container"/>')
 *    resultTemplate(string): HTML template for the element that will contain file information. ('<div class="dz-notice"><p>Drop files here...</p></div><div class="upload-previews"/>')
 *    autoCleanResults(boolean): condition value for the file preview in div element to fadeout after file upload is completed. (true)
 *    previewsContainer(selector): JavaScript selector for file preview in div element. (.upload-previews)
 *    container(selector): JavaScript selector for where to put upload stuff into in case of form. If not provided it will be place before the first submit button. ('')
 *    relatedItems(object): Related items pattern options. Will only use only if relativePath is used to use correct upload destination ({ attributes: ["UID", "Title", "Description", "getURL", "portal_type", "path", "ModificationDate"], batchSize: 20, basePath: "/", vocabularyUrl: null, width: 500, maximumSelectionSize: 1, placeholder: "Search for item on site..." })
 *
 * Documentation:
 *
 *    # On a div element
 *
 *    {{ example-1 }}
 *
 * Example: example-1
 *    <div class="pat-upload" data-pat-upload='{"url": "/upload",
 *                                              "relatedItems": {
 *                                                  "vocabularyUrl": "/relateditems-test.json"
 *                                              }}'>
 *      <div>
 *        <p>Something here that is useful</p>
 *        <p>Something else here that is useful</p>
 *        <p>Another thing here that is useful</p>
 *      </div>
 *    </div>
 *
 */


define([
  'jquery',
  'underscore',
  'mockup-patterns-base',
  'mockup-patterns-relateditems',
  'dropzone',
  'text!mockup-patterns-upload-url/templates/upload.xml',
  'text!mockup-patterns-upload-url/templates/preview.xml',
  'translate'
], function($, _, Base, RelatedItems, Dropzone,
            UploadTemplate, PreviewTemplate, _t) {
  'use strict';

  /* we do not want this plugin to auto discover */
  Dropzone.autoDiscover = false;

  var UploadPattern = Base.extend({
    name: 'upload',
    trigger: '.pat-upload',
    defaults: {
      showTitle: true,
      url: null, // XXX MUST provide url to submit to OR be in a form
      className: 'upload',
      wrap: false,
      wrapperTemplate: '<div class="upload-wrapper"/>',
      fileaddedClassName: 'dropping',
      useTus: false,
      container: '',
      ajaxUpload: true,

      paramName: 'file',
      addRemoveLinks: false,
      autoCleanResults: true,
      previewsContainer: '.previews',
      previewTemplate: null,
      maxFiles: null,
      maxFilesize: 99999999, // let's not have a max by default...

      relatedItems: {
        // UID attribute is required here since we're working with related items
        attributes: ['UID', 'Title', 'Description', 'getURL', 'portal_type', 'path', 'ModificationDate'],
        batchSize: 20,
        basePath: '/',
        vocabularyUrl: null,
        width: 500,
        maximumSelectionSize: 1,
        selectableTypes: ['Folder']
      }
    },

    init: function() {
      var self = this,
          template = UploadTemplate;

      // TODO: find a way to make this work in firefox (and IE)
      $(document).bind('paste', function(e){
        var oe = e.originalEvent;
        var items = oe.clipboardData.items;
        if (items) {
          for (var i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
              var blob = items[i].getAsFile();
              self.dropzone.addFile(blob);
            }
          }
        }
      });
      // values that will change current processing
      self.currentPath = self.options.currentPath;
      self.currentFile = 0;

      template = _.template(template, {_t: _t});
      self.$el.addClass(self.options.className);
      self.$el.append(template);

      self.$progress = $('.progress-bar-success', self.$el);

      if (!self.options.showTitle) {
        self.$el.find('h2.title').hide();
      }

      if (!self.options.ajaxUpload) {
        // no ajax upload, drop the fallback
        $('.fallback', this.$el).remove();
        if (this.$el.hasClass('.upload-container')) {
          this.$el.addClass('no-ajax-upload');
        } else {
          this.$el.closest('.upload-container').addClass('no-ajax-upload');
        }
      }

      if (self.options.wrap) {
        self.$el.wrap(self.options.wrapperTemplate);
        self.$el = self.$el.parent();
      }

      if (self.options.baseUrl && self.options.relativePath){
        // only use related items if we can generate paths based urls
        self.$pathInput = $('input[name="location"]', self.$el);
        self.relatedItems = self.setupRelatedItems(self.$pathInput);
      } else {
        $('input[name="location"]', self.$el).parent().remove();
        self.relatedItems = null;
      }

      self.$dropzone = $('.upload-area', self.$el);

      $('button.browse', self.$el).click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        if(!self.options.maxFiles || self.dropzone.files.length < self.options.maxFiles){
          self.dropzone.hiddenFileInput.click();
        }
      });

      var dzoneOptions = this.getDzoneOptions();

      try {
        // if init of Dropzone fails it says nothing and
        // it fails silently. Using this block we make sure
        // that if you break it w/ some weird or missing option
        // you can get a proper log of it
        //
        self.dropzone = new Dropzone(self.$dropzone[0], dzoneOptions);
      } catch (e) {
        if (window.DEBUG) {
          // log it!
          console.log(e);
        }
        throw e;
      }

      self.dropzone.on('maxfilesreached', function(){
        self.showHideControls();
      });

      self.dropzone.on('addedfile', function(/* file */) {
        self.showHideControls();
      });

      self.dropzone.on('removedfile', function() {
        self.showHideControls();
      });

      self.dropzone.on('success', function(e, response){
        // Trigger event 'uploadAllCompleted' and pass the server's reponse and
        // the path uid. This event can be listened to by patterns using the
        // upload pattern, e.g. the TinyMCE pattern's link plugin.
        var data;
        try{
          data = $.parseJSON(response);
        }catch(ex){
          data = response;
        }
        self.$el.trigger('uploadAllCompleted', {
          'data': data,
          'path_uid': (self.$pathInput) ? self.$pathInput.val() : null
        });
      });

      if (self.options.autoCleanResults) {
        self.dropzone.on('complete', function(file) {
          if (file.status === Dropzone.SUCCESS){
            setTimeout(function() {
              $(file.previewElement).fadeOut();
            }, 3000);
          }
        });
      }

      self.dropzone.on('complete', function(file) {
        if (file.status === Dropzone.SUCCESS && self.dropzone.files.length === 1) {
          self.showHideControls();
        }
      });

      self.dropzone.on('error', function(file, response, xmlhr) {
        if (typeof(xmlhr) !== 'undefined' && xmlhr.status !== 403){
          // If error other than 403, just print a generic message
          $('.dz-error-message span', file.previewElement).html(_t('The file transfer failed'));
        }
      });

      self.dropzone.on('totaluploadprogress', function(pct) {
        // need to caclulate total pct here in reality since we're manually
        // processing each file one at a time.
        pct = ((((self.currentFile - 1) * 100) + pct) / (self.dropzone.files.length * 100)) * 100;
        self.$progress.attr('aria-valuenow', pct).css('width', pct + '%');
      });

      $('.upload-all', self.$el).click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        self.processUpload({
          finished: function() {
            self.$progress.attr('aria-valuenow', 0).css('width', '0%');
          }
        });
      });
      if(self.options.clipboardfile){
        self.dropzone.addFile(self.options.clipboardfile);
      }
    },

    showHideControls: function(){
      /* we do this delayed because this can be called multiple times
         AND we need to do this hide/show AFTER dropzone is done with
         all it's own events. This is NASTY but the only way we can
         enforce some numFiles with dropzone! */
      var self = this;
      if(self._showHideTimeout){
        clearTimeout(self._showHideTimeout);
      }
      self._showHideTimeout = setTimeout(function(){
        self._showHideControls();
      }, 50);
    },

    _showHideControls: function(){
      var self = this;
      var $controls = $('.controls', self.$el);
      var $browse = $('.browse-select', self.$el);
      var $input = $('.dz-hidden-input');

      if(self.options.maxFiles){
        if(self.dropzone.files.length < self.options.maxFiles){
          $browse.show();
          $input.prop('disabled', false);
        }else{
          $browse.hide();
          $input.prop('disabled', true);
        }
      }
      if(self.dropzone.files.length > 0){
        $controls.fadeIn('slow');
        var file = self.dropzone.files[0];
        $('.dz-error-message span', file.previewElement).html('');
      }else{
        $controls.fadeOut('slow');
      }
    },

    pathJoin: function() {
      var parts = [];
      _.each(arguments, function(part) {
        if (!part){
          return;
        }
        if (part[0] === '/'){
          part = part.substring(1);
        }
        if (part[part.length - 1] === '/'){
          part = part.substring(0, part.length - 1);
        }
        parts.push(part);
      });
      return parts.join('/');
    },

    getUrl: function() {

      var self = this;
      var url = self.options.url;
      if (!url) {
        if (self.options.baseUrl && self.options.relativePath){
          url = self.options.baseUrl;
          if (url[url.length - 1] !== '/'){
            url = url + '/';
          }
          url = url + self.pathJoin(self.currentPath, self.options.relativePath);
        } else {
          var $form = self.$el.parents('form');
          if ($form.length > 0){
            url = $form.attr('action');
          } else {
            url = window.location.href;
          }
        }
      }
      return url;
    },

    getDzoneOptions: function() {
      var self = this;

      // This pattern REQUIRE dropzone to be clickable
      self.options.clickable = true;

      var options = $.extend({}, self.options);
      options.url = self.getUrl();

      // XXX force to only upload one to the server at a time,
      // right now we don't support multiple for backends
      options.uploadMultiple = false;

      delete options.wrap;
      delete options.wrapperTemplate;
      delete options.resultTemplate;
      delete options.autoCleanResults;
      delete options.fileaddedClassName;
      delete options.useTus;

      if (self.options.previewsContainer) {
        /*
         * if they have a select but it's not an id, let's make an id selector
         * so we can target the correct container. dropzone is weird here...
         */
        var $preview = self.$el.find(self.options.previewsContainer);
        if ($preview.length > 0) {
          options.previewsContainer = $preview[0];
        }
      }

      // XXX: do we need to allow this?
      options.autoProcessQueue = false;
      // options.addRemoveLinks = true;  // we show them in the template
      options.previewTemplate = PreviewTemplate;

      // if our element is a form we should force some values
      // https://github.com/enyo/dropzone/wiki/Combine-normal-form-with-Dropzone
      return options;
    },

    processUpload: function(options) {
      if (!options){
        options = {};
      }

      var self = this,
          processing = false,
          useTus = self.options.useTus,
          fileaddedClassName = self.options.fileaddedClassName,
          finished = options.finished;

      self.currentFile = 0;

      function process() {
        processing = true;
        if (self.dropzone.files.length === 0) {
          processing = false;
        }

        var file = self.dropzone.files[0];
        if (processing && file.status === Dropzone.ERROR){
          // Put the file back as "queued" for retrying
          file.status = Dropzone.QUEUED;
          processing = false;
        }

        if (!processing){
          self.$el.removeClass(fileaddedClassName);
          if (finished !== undefined && typeof(finished) === 'function'){
            finished();
          }
          return;
        }

        if ([Dropzone.SUCCESS, Dropzone.CANCELED]
            .indexOf(file.status) !== -1) {
          // remove it
          self.dropzone.removeFile(file);
          process();
        } else if (file.status !== Dropzone.UPLOADING) {
          // start processing file
          if (useTus && window.tus) {
            // use tus upload if installed
            self.handleTusUpload(file);
          } else {
            // otherwise, just use dropzone to process
            self.currentFile += 1;
            self.dropzone.processFile(file);
          }
          setTimeout(process, 100);
        } else {
          // currently processing
          setTimeout(process, 100);
        }
      }
      process();
    },

    handleTusUpload: function(file) {
      /* this needs fixing... */
      var self = this,
          $preview = $(file.previewElement),
          chunkSize = 1024 * 1024 * 5; // 5mb chunk size

      file.status = Dropzone.UPLOADING;

      window.tus.upload(file, {
        endpoint: self.dropzone.options.url,
        headers: {
          'FILENAME': file.name
        },
        chunkSize: chunkSize
      }).fail(function() {
        if(window.DEBUG){
          console.alert(_t('Error uploading with TUS resumable uploads'));
        }
        file.status = Dropzone.ERROR;
      }).progress(function(e, bytesUploaded, bytesTotal) {
        var percentage = (bytesUploaded / bytesTotal * 100);
        self.$progress.attr('aria-valuenow', percentage).css('width', percentage + '%');
        self.$progress.html(_t('uploading...') + '<br />' +
                            self.formatBytes(bytesUploaded) +
                            ' / ' + self.formatBytes(bytesTotal));
      }).done(function(url, file) {
        file.status = Dropzone.SUCCESS;
        self.dropzone.emit('success', file);
        self.dropzone.emit('complete', file);
      });
    },

    formatBytes: function(bytes) {
      var kb = Math.round(bytes / 1024);
      if (kb < 1024) {
        return kb + ' KiB';
      }
      var mb = Math.round(kb / 1024);
      if (mb < 1024) {
        return mb + ' MB';
      }
      return Math.round(mb / 1024) + ' GB';
    },

    setPath: function(path){
      var self = this;
      self.currentPath = path;
      self.options.url = null;
      self.options.url = self.dropzone.options.url = self.getUrl();
    },

    setupRelatedItems: function($input) {
      var self = this;
      var options = self.options.relatedItems;
      if (self.options.initialFolder){
        $input.attr('value', self.options.initialFolder);
      }
      var ri = new RelatedItems($input, options);
      ri.$el.on('change', function() {
        var result = $(this).select2('data');
        var path = null;
        if (result.length > 0){
          path = result[0].path;
        }
        self.setPath(path);
      });
      return ri;
    }

  });

  return UploadPattern;

});
