define([
  'jquery',
  'mockup-patterns-base',
  'pat-registry',
  'mockup-utils',
  'jquery.cookie'
], function ($, Base, Registry, utils) {
  'use strict';

  var Toolbar = Base.extend({
    name: 'toolbar',
    trigger: '.pat-toolbar',
    defaults: {
      containerSelector: '#edit-zone',
      classNames: {
        logo: 'plone-toolbar-logo',
        left: 'plone-toolbar-left-default',
        leftExpanded: 'plone-toolbar-left-expanded',
        top: 'plone-toolbar-top-default',
        topExpanded: 'plone-toolbar-top-expanded',
        expanded: 'expanded',
        active: 'active',
        compressed: 'plone-toolbar-compressed'
      },
      cookieName: 'plone-toolbar'
    },
    setupMobile: function(){
      var that = this;
      // $( 'html' ).has('.plone-toolbar-left').css({'margin-left':'0','margin-top':'0','margin-right':'0'});
      // $( 'html' ).has('.plone-toolbar-top').css({'margin-left':'0','margin-top':'0','margin-right':'0'});
      // $( 'html' ).has('.plone-toolbar-left.expanded').css({'margin-left':'0','margin-top':'0','margin-right':'0'});
      // $( 'body' ).css('margin-left: 0px');
      that.$container.css('right', '-120px');
      $('.' + that.options.classNames.logo, that.$container).click(function() {
        var $el = $(this);
        if ($el.hasClass('open')){
          that.$container.css('right', '-120px');
          $('html').css('margin-left', '0');
          $('html').css('margin-right', '0');
          $el.removeClass('open');
          $('nav li', that.$container).removeClass(that.options.classNames.active);
        } else {
          that.$container.css('right', '0');
          $el.addClass('open');
          $('html').css('margin-left', '-120px');
          $( 'html' ).css('margin-right', '120px');
        }
      });
      $('nav li', that.$container).has( 'a .plone-toolbar-caret' ).click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        var $el = $(this);
        if ($el.hasClass(that.options.classNames.active)) {
          that.$container.css('right', '0');
          $('html').css('margin-left', '-120px');
          $('html').css('margin-right', '120px');
          $('nav li', that.$container).removeClass(that.options.classNames.active);
        } else {
          $('nav li', that.$container).removeClass(that.options.classNames.active);
          $el.addClass(that.options.classNames.active);
          that.$container.css('right', '180px');
          $('html').css('margin-left', '-300px');
          $('html').css('margin-right', '300px');
        }
      });
    },
    setupDesktop: function(){
      var that = this;
      var toolbar_cookie = $.cookie(that.options.cookieName);
      that.state = toolbar_cookie;
      that.$container.attr('class', toolbar_cookie);

      $('.' + that.options.classNames.logo, that.$container).on('click', function() {
        if (that.state) {
          if (that.state.indexOf('expanded') != -1) {
            // Switch to default (only icons)
            that.$container.removeClass(that.options.classNames.expanded);
            $('nav li', that.$container).removeClass(that.options.classNames.active);
            if (that.state.indexOf('left') != -1) {
              $('body').addClass(that.options.classNames.left);
              $('body').removeClass(that.options.classNames.leftExpanded);
            } else {
              $('body').addClass(that.options.classNames.top);
              $('body').removeClass(that.options.classNames.topExpanded);
            }
            $.cookie(that.options.cookieName, that.$container.attr('class'), {path: '/'});
            that.state = that.state.replace(' ' + that.options.classNames.expanded, '');
          } else {
            // Switch to expanded
            that.$container.addClass(that.options.classNames.expanded);
            $('nav li', that.$container).removeClass(that.options.classNames.active);
            if (that.state.indexOf('left') != -1) {
              $('body').addClass(that.options.classNames.leftExpanded);
              $('body').removeClass(that.options.classNames.left);
            } else {
              $('body').addClass(that.options.classNames.topExpanded);
              $('body').removeClass(that.options.classNames.top);
            }
            $.cookie(that.options.cookieName, that.$container.attr('class'), {path: '/'});
            that.state = that.state + ' ' + that.options.classNames.expanded;
          }
        } else {
          // Cookie not set, assume default (only icons)
          that.state = 'pat-toolbar plone-toolbar-left';
          // Switch to expanded left
          that.$container.addClass(that.options.classNames.expanded);
          $('nav li', that.$container).removeClass(that.options.classNames.active);
          $('body').addClass(that.options.classNames.leftExpanded);
          $('body').removeClass(that.options.classNames.left);
          $.cookie(that.options.cookieName, that.$container.attr('class'), {path: '/'});
          that.state = that.state + ' ' + that.options.classNames.expanded;
        }
      });

      // Switch to compressed
      $('.' + that.options.classNames.logo, that.$container).on('dblclick', function() {
        if (that.state) {
          if (that.state.indexOf('compressed') != -1) {
            // Switch to default (only icons) not compressed
            that.$container.removeClass('compressed');
            if (that.state.indexOf('left') != -1) {
              $('body').addClass(that.options.classNames.left);
              $('body').removeClass(that.options.classNames.compressed);
            } else {
              $('body').addClass(that.options.classNames.top);
              $('body').removeClass(that.options.classNames.compressed);
            }
            $.cookie(that.options.cookieName, that.$container.attr('class'), {path: '/'});
            that.state = that.state.replace(' ' + that.options.classNames.expanded, '');
          } else {
            // Switch to compressed
            that.$container.addClass('compressed');
            if (that.state.indexOf('left') != -1) {
              $('body').addClass(that.options.classNames.compressed);
              $('body').removeClass(that.options.classNames.left);
              $('body').removeClass(that.options.classNames.leftExpanded);
            } else {
              $('body').addClass(that.options.classNames.compressed);
              $('body').removeClass(that.options.classNames.top);
              $('body').removeClass(that.options.classNames.topExpanded);
            }
            $.cookie(that.options.cookieName, that.$container.attr('class'), {path: '/'});
            that.state = that.state + ' compressed';
          }
        } else {
          // Cookie not set, assume default (only icons)
          // Switch to compressed
          that.$container.addClass('compressed');
          $('body').addClass(that.options.classNames.compressed);
          $('body').removeClass(that.options.classNames.left);
          $('body').removeClass(that.options.classNames.leftExpanded);
          $.cookie(that.options.cookieName, that.$container.attr('class'), {path: '/'});
          that.state = that.state + ' compressed';
        }
      });


      $('nav > ul > li li', that.$container).on('click', function(event) {
        event.stopImmediatePropagation();
      });

      // active
      $('nav > ul > li', that.$container).has( 'a .plone-toolbar-caret' ).on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var hasClass = $(this).hasClass(that.options.classNames.active);
        // always close existing
        $('nav li', that.$container).removeClass(that.options.classNames.active);
        if (!hasClass) {
          // open current selected if not already open
          $(this).addClass(that.options.classNames.active);
          that.padPulloutContent($(this));
        }
      });

      $('body').on('click', function(event) {
        if (!($(this).parent(that.options.containerSelector).length > 0)) {
          $('nav > ul > li', that.$container).each(function(key, element){
            $(element).removeClass(that.options.classNames.active);
          });
        }
      });
      that.setHeight();
    },
    padPulloutContent: function($li){
      // try to place content as close to the user click as possible
      var $content = $('> ul', $li);
      var $inner = $content.find('> *');
      var $first = $inner.first();
      var $last = $inner.last();
      var insideHeight = ($last.position().top - $first.position().top) + $last.outerHeight();
      var height = $content.outerHeight();

      var itemLocation = $li.position().top || $li.offset().top;  // depends on positioning
      // padding-top + insideHeight should equal total height
      $content.css({
        'padding-top': Math.min(itemLocation, height - insideHeight)
      });
    },
    setHeight: function(){
      $('.plone-toolbar-main', this.$container).css({height: ''});
      var $el = $('.plone-toolbar-main', this.$container),
        scrollTop = $(window).scrollTop(),
        scrollBot = scrollTop + $(window).height(),
        elTop = $el.offset().top,
        elBottom = elTop + $el.outerHeight(),
        visibleTop = elTop < scrollTop ? scrollTop : elTop,
        visibleBottom = elBottom > scrollBot ? scrollBot : elBottom;
      // unset height first
      $('.plone-toolbar-main', this.$container).height(
        visibleBottom - visibleTop - $('#portal-personaltools').outerHeight());
    },
    init: function () {
      var that = this;
      that.$container = $(that.options.containerSelector);
      var toolbar_cookie = $.cookie(that.options.cookieName);
      that.state = toolbar_cookie;

      if ($(window).width() < '768'){//mobile
        that.setupMobile();
      }
      else { // not mobile
        that.setupDesktop();
      }
      this.$el.addClass('initialized');

      /* folder contents changes the context.
         This is for usability so the menu changes along with
         the folder contents context */
      $('body').off('structure-url-changed').on('structure-url-changed', function (e, path) {
        $.ajax({
          url: $('body').attr('data-portal-url') + path + '/@@render-toolbar'
        }).done(function(data){
          var $el = $(utils.parseBodyTag(data));
          that.$el.replaceWith($el);
          Registry.scan($el);
        });
      });

      $(window).on('resize', function(){
        that.setHeight();
      });
    },

  });

  return Toolbar;
});
