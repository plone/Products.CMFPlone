/* Pattern utils
 */


define([
  'jquery'
], function($) {
  'use strict';

  var QueryHelper = function(options) {
    /* if pattern argument provided, it can implement the interface of:
      *    - browsing: boolean if currently browsing
      *    - currentPath: string of current path to apply to search if browsing
      *    - basePath: default path to provide if no subpath used
      */

    var self = this;
    var defaults = {
      pattern: null, // must be passed in
      vocabularyUrl: null,
      searchParam: 'SearchableText', // query string param to pass to search url
      attributes: ['UID', 'Title', 'Description', 'getURL', 'portal_type'],
      batchSize: 10, // number of results to retrive
      baseCriteria: [],
      sort_on: 'is_folderish',
      sort_order: 'reverse',
      pathDepth: 1
    };
    self.options = $.extend({}, defaults, options);
    self.pattern = self.options.pattern;
    if (self.pattern === undefined || self.pattern === null) {
      self.pattern = {
        browsing: false,
        basePath: '/'
      };
    }

    if (self.options.url && !self.options.vocabularyUrl) {
      self.options.vocabularyUrl = self.options.url;
    } else if (self.pattern.vocabularyUrl) {
      self.options.vocabularyUrl = self.pattern.vocabularyUrl;
    }
    if (self.options.vocabularyUrl !== undefined &&
        self.options.vocabularyUrl !== null) {
      self.valid = true;
    } else {
      self.valid = false;
    }

    self.getCurrentPath = function() {
      var pattern = self.pattern;
      var currentPath;
      /* If currentPath is set on the QueryHelper object, use that first.
       * Then, check on the pattern.
       * Finally, see if it is a function and call it if it is.
       */
      if (self.currentPath) {
        currentPath = self.currentPath;
      } else {
        currentPath = pattern.currentPath;
      }
      if (typeof currentPath  === 'function') {
        currentPath = currentPath();
      }
      var path = currentPath;
      if (!path) {
        if (pattern.basePath) {
          path = pattern.basePath;
        } else if (pattern.options.basePath) {
          path = pattern.options.basePath;
        } else {
          path = '/';
        }
      }
      return path;
    };

    self.getCriterias = function(term, options) {
      if (options === undefined) {
        options = {};
      }
      options = $.extend({}, {
        useBaseCriteria: true,
        additionalCriterias: []
      }, options);

      var criterias = [];
      if (options.useBaseCriteria) {
        criterias = self.options.baseCriteria.slice(0);
      }
      if (term) {
        term += '*';
        criterias.push({
          i: self.options.searchParam,
          o: 'plone.app.querystring.operation.string.contains',
          v: term
        });
      }
      if(options.searchPath){
        criterias.push({
          i: 'path',
          o: 'plone.app.querystring.operation.string.path',
          v: options.searchPath + '::' + self.options.pathDepth
        });
      }else if (self.pattern.browsing) {
        criterias.push({
          i: 'path',
          o: 'plone.app.querystring.operation.string.path',
          v: self.getCurrentPath() + '::' + self.options.pathDepth
        });
      }
      criterias = criterias.concat(options.additionalCriterias);
      return criterias;
    };

    self.getBatch = function(page) {
      if (!page) {
        page = 1;
      }
      return {
        page: page,
        size: self.options.batchSize
      };
    };

    self.selectAjax = function() {
      return {
        url: self.options.vocabularyUrl,
        dataType: 'JSON',
        quietMillis: 100,
        data: function(term, page) {
          return self.getQueryData(term, page);
        },
        results: function (data, page) {
          var more = (page * 10) < data.total; // whether or not there are more results available
          // notice we return the value of more so Select2 knows if more results can be loaded
          return {results: data.results, more: more};
        }
      };
    };

    self.getUrl = function() {
      var url = self.options.vocabularyUrl;
      if (url.indexOf('?') === -1) {
        url += '?';
      } else {
        url += '&';
      }
      return url + $.param(self.getQueryData());
    };

    self.getQueryData = function(term, page) {
      var data = {
        query: JSON.stringify({
          criteria: self.getCriterias(term),
          sort_on: self.options.sort_on,
          sort_order: self.options.sort_order
        }),
        attributes: JSON.stringify(self.options.attributes)
      };
      if (page) {
        data.batch = JSON.stringify(self.getBatch(page));
      }
      return data;
    };

    self.search = function(term, operation, value, callback, useBaseCriteria, type) {
      if (useBaseCriteria === undefined) {
        useBaseCriteria = true;
      }
      if(type === undefined){
        type = 'GET';
      }
      var criteria = [];
      if (useBaseCriteria) {
        criteria = self.options.baseCriteria.slice(0);
      }
      criteria.push({
        i: term,
        o: operation,
        v: value
      });
      var data = {
        query: JSON.stringify({ criteria: criteria }),
        attributes: JSON.stringify(self.options.attributes)
      };
      $.ajax({
        url: self.options.vocabularyUrl,
        dataType: 'JSON',
        data: data,
        type: type,
        success: callback
      });
    };

    return self;
  };

  var Loading = function(options){
    /*
     * Options:
     *   backdrop(pattern): if you want to have the progress indicator work
     *                      seamlessly with backdrop pattern
     *   zIndex(integer or function): to override default z-index used
     */
    var self = this;
    self.className = 'plone-loader';
    var defaults = {
      backdrop: null,
      zIndex: 10005 // can be a function
    };
    if(!options){
      options = {};
    }
    self.options = $.extend({}, defaults, options);
    self.$el = $('.' + self.className);
    if(self.$el.length === 0){
      self.$el = $('<div><div></div></div>');
      self.$el.addClass(self.className).hide().appendTo('body');
    }

    self.show = function(closable){
      self.$el.show();
      var zIndex = self.options.zIndex;
      if (typeof(zIndex) === 'function') {
        zIndex = Math.max(zIndex(), 10005);
      }else{
        // go through all modals and backdrops and make sure we have a higher
        // z-index to use
        zIndex = 10005;
        $('.plone-modal-wrapper,.plone-modal-backdrop').each(function(){
          zIndex = Math.max(zIndex, $(this).css('zIndex') || 10005);
        });
        zIndex += 1;
      }
      self.$el.css('zIndex', zIndex);

      if (closable === undefined) {
        closable = true;
      }
      if (self.options.backdrop) {
        self.options.backdrop.closeOnClick = closable;
        self.options.backdrop.closeOnEsc = closable;
        self.options.backdrop.init();
        self.options.backdrop.show();
      }
    };

    self.hide = function(){
      self.$el.hide();
    };

    return self;
  };

  var generateId = function(prefix){
    if (prefix === undefined) {
      prefix = 'id';
    }
    return prefix + (Math.floor((1 + Math.random()) * 0x10000)
        .toString(16).substring(1));
  };

  return {
    generateId: generateId,
    parseBodyTag: function(txt) {
      return $((/<body[^>]*>((.|[\n\r])*)<\/body>/im).exec(txt)[0]
          .replace('<body', '<div').replace('</body>', '</div>')).eq(0).html();
    },
    setId: function($el, prefix) {
      if (prefix === undefined) {
        prefix = 'id';
      }
      var id = $el.attr('id');
      if (id === undefined) {
        id = generateId(prefix);
      } else {
        /* hopefully we don't screw anything up here... changing the id
         * in some cases so we get a decent selector */
        id = id.replace(/\./g, '-');
      }
      $el.attr('id', id);
      return id;
    },
    bool: function(val) {
      if (typeof val === 'string') {
        val = $.trim(val).toLowerCase();
      }
      return ['true', true, 1].indexOf(val) !== -1;
    },
    QueryHelper: QueryHelper,
    Loading: Loading,
    // provide default loader
    loading: new Loading(),
    getAuthenticator: function() {
      var $el = $('input[name="_authenticator"]');
      if($el.length === 0){
        $el = $('a[href*="_authenticator"]');
        if($el.length > 0){
          return $el.attr('href').split('_authenticator=')[1];
        }
        return '';
      }else{
        return $el.val();
      }
    },
    featureSupport: {
      /*
        well tested feature support for things we use in mockup.
        All gathered from: http://diveintohtml5.info/everything.html
        Alternative to using some form of modernizr.
      */
      dragAndDrop: function(){
        return 'draggable' in document.createElement('span');
      },
      fileApi: function(){
        return typeof FileReader != 'undefined'; // jshint ignore:line
      },
      history: function(){
        return !!(window.history && window.history.pushState);
      }
    }
  };
});
