define([
  'jquery',
  'mockup-patterns-base',
  'jquery.cookie'
], function ($, Base) {
  'use strict';

  var Toolbar = Base.extend({
    name: 'toolbar',
    trigger: '.pat-toolbar',
    init: function () {
      if ($(window).width() < '768'){//mobile
        // $( 'html' ).has('.plone-toolbar-left').css({'margin-left':'0','margin-top':'0','margin-right':'0'});
        // $( 'html' ).has('.plone-toolbar-top').css({'margin-left':'0','margin-top':'0','margin-right':'0'});
        // $( 'html' ).has('.plone-toolbar-left.expanded').css({'margin-left':'0','margin-top':'0','margin-right':'0'});
        // $( 'body' ).css('margin-left: 0px');
        $('#edit-zone').css('right', '-120px');
        $( '#edit-zone .plone-toolbar-logo' ).click(function() {
          if ($(this).hasClass('open')){
            $( '#edit-zone' ).css('right', '-120px');
            $( 'html' ).css('margin-left', '0');
            $( 'html' ).css('margin-right', '0');
            $(this).removeClass('open');
            $( '#edit-zone nav li' ).removeClass('active');
          } else {
            $( '#edit-zone' ).css('right', '0');
            $(this).addClass('open');
            $( 'html' ).css('margin-left', '-120px');
            $( 'html' ).css('margin-right', '120px');
          }
        });
        $( '#edit-zone nav li' ).has( 'a .plone-toolbar-caret' ).click(function(e) {
          e.preventDefault();
          e.stopPropagation();
          if ($(this).hasClass('active')) {
            $( '#edit-zone' ).css('right', '0');
            $( 'html' ).css('margin-left', '-120px');
            $( 'html' ).css('margin-right', '120px');
            $( '#edit-zone nav li' ).removeClass('active');
          } else {
            $( '#edit-zone nav li' ).removeClass('active');
            $(this).addClass('active');
            $( '#edit-zone' ).css('right', '180px');
            $( 'html' ).css('margin-left', '-300px');
            $( 'html' ).css('margin-right', '300px');
          }
        });
      }
      else { // not mobile
        var toolbar_cookie = $.cookie('plone-toolbar');
        window.plonetoolbar_state = toolbar_cookie;
        $('#edit-zone').attr('class', toolbar_cookie);

        $( '#edit-zone .plone-toolbar-logo' ).on('click', function() {
          if (window.plonetoolbar_state) {
            if (window.plonetoolbar_state.indexOf('expanded') != -1) {
              // Switch to default (only icons)
              $( '#edit-zone' ).removeClass('expanded');
              $( '#edit-zone nav li' ).removeClass('active');
              if (window.plonetoolbar_state.indexOf('left') != -1) {
                $('body').addClass('plone-toolbar-left-default');
                $('body').removeClass('plone-toolbar-left-expanded');
              } else {
                $('body').addClass('plone-toolbar-top-default');
                $('body').removeClass('plone-toolbar-top-expanded');
              }
              $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
              window.plonetoolbar_state = window.plonetoolbar_state.replace(' expanded', '');
            } else {
              // Switch to expanded
              $( '#edit-zone' ).addClass('expanded');
              $( '#edit-zone nav li' ).removeClass('active');
              if (window.plonetoolbar_state.indexOf('left') != -1) {
                $('body').addClass('plone-toolbar-left-expanded');
                $('body').removeClass('plone-toolbar-left-default');
              } else {
                $('body').addClass('plone-toolbar-top-expanded');
                $('body').removeClass('plone-toolbar-top-default');
              }
              $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
              window.plonetoolbar_state = window.plonetoolbar_state + ' expanded';
            }
          } else {
            // Cookie not set, assume default (only icons)
            window.plonetoolbar_state = 'pat-toolbar plone-toolbar-left';
            // Switch to expanded left
            $( '#edit-zone' ).addClass('expanded');
            $( '#edit-zone nav li' ).removeClass('active');
            $('body').addClass('plone-toolbar-left-expanded');
            $('body').removeClass('plone-toolbar-left-default');
            $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
            window.plonetoolbar_state = window.plonetoolbar_state + ' expanded';
          }
        });

        // Switch to compressed
        $( '#edit-zone .plone-toolbar-logo' ).on('dblclick', function() {
          if (window.plonetoolbar_state) {
            if (window.plonetoolbar_state.indexOf('compressed') != -1) {
              // Switch to default (only icons) not compressed
              $( '#edit-zone' ).removeClass('compressed');
              if (window.plonetoolbar_state.indexOf('left') != -1) {
                $('body').addClass('plone-toolbar-left-default');
                $('body').removeClass('plone-toolbar-compressed');
              } else {
                $('body').addClass('plone-toolbar-top-default');
                $('body').removeClass('plone-toolbar-compressed');
              }
              $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
              window.plonetoolbar_state = window.plonetoolbar_state.replace(' expanded', '');
            } else {
              // Switch to compressed
              $( '#edit-zone' ).addClass('compressed');
              if (window.plonetoolbar_state.indexOf('left') != -1) {
                $('body').addClass('plone-toolbar-compressed');
                $('body').removeClass('plone-toolbar-left-default');
                $('body').removeClass('plone-toolbar-left-expanded');
              } else {
                $('body').addClass('plone-toolbar-compressed');
                $('body').removeClass('plone-toolbar-top-default');
                $('body').removeClass('plone-toolbar-top-expanded');
              }
              $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
              window.plonetoolbar_state = window.plonetoolbar_state + ' compressed';
            }
          } else {
            // Cookie not set, assume default (only icons)
            // Switch to compressed
            $( '#edit-zone' ).addClass('compressed');
            $('body').addClass('plone-toolbar-compressed');
            $('body').removeClass('plone-toolbar-left-default');
            $('body').removeClass('plone-toolbar-left-expanded');
            $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
            window.plonetoolbar_state = window.plonetoolbar_state + ' compressed';
          }
        });


        $( '#edit-zone nav > ul > li li' ).on('click', function(event) {
          event.stopImmediatePropagation();
        });

        // active
        $( '#edit-zone nav > ul > li' ).has( 'a .plone-toolbar-caret' ).on('click', function(event) {
          event.preventDefault();
          event.stopPropagation();
          if ($(this).hasClass('active')) {
            $( '#edit-zone nav li' ).removeClass('active');
          } else {
            $('#edit-zone nav li').removeClass('active');
            $(this).addClass('active');
          }
        });

        $('body').on('click', function(event) {
          if (!($(this).parent('#edit-zone').length > 0)) {
            $('#edit-zone nav > ul > li').each(function(key, element){
              $(element).removeClass('active');
            });
          }
        });

        // top/left switcher
        $( '#edit-zone .plone-toolbar-switcher' ).on('click', function() {
          if (window.plonetoolbar_state) {
            if (window.plonetoolbar_state.indexOf('top') != -1) {
              // from top to left
              $( '#edit-zone' ).addClass('plone-toolbar-left');
              $( '#edit-zone' ).removeClass('plone-toolbar-top');
              if (window.plonetoolbar_state.indexOf('expanded') != -1) {
                $('body').addClass('plone-toolbar-left-expanded');
                $('body').removeClass('plone-toolbar-top-expanded');
              } else {
                $('body').addClass('plone-toolbar-left-default');
                $('body').removeClass('plone-toolbar-top-default');
              }
              $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
              window.plonetoolbar_state = window.plonetoolbar_state.replace('plone-toolbar-top', 'plone-toolbar-left');
            } else {
              // from left to top
              $( '#edit-zone' ).addClass('plone-toolbar-top');
              $( '#edit-zone' ).removeClass('plone-toolbar-left');
              if (window.plonetoolbar_state.indexOf('expanded') != -1) {
                $('body').addClass('plone-toolbar-top-expanded');
                $('body').removeClass('plone-toolbar-left-expanded');
              } else {
                $('body').addClass('plone-toolbar-top-default');
                $('body').removeClass('plone-toolbar-left-default');
              }
              $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
              window.plonetoolbar_state = window.plonetoolbar_state.replace('plone-toolbar-left', 'plone-toolbar-top');
            }
          } else {
            // Cookie not set, assume left default (only icons)
            window.plonetoolbar_state = 'pat-toolbar plone-toolbar-left';
            // Switch to top
            $( '#edit-zone' ).addClass('plone-toolbar-left');
            $( '#edit-zone' ).removeClass('plone-toolbar-top');
            $('body').addClass('plone-toolbar-top-default');
            $('body').removeClass('plone-toolbar-left-default');
            $.cookie('plone-toolbar', $('#edit-zone').attr('class'), {path: '/'});
            window.plonetoolbar_state = window.plonetoolbar_state.replace('plone-toolbar-left', 'plone-toolbar-top');
          }

        });
      }
      this.$el.addClass('initialized');
    }
  });

  return Toolbar;
});
