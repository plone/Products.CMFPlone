define([
  'jquery',
  'mockup-patterns-base'
], function ($, Base) {
  'use strict';

  var Toolbar = Base.extend({
    name: 'toolbar',
    init: function () {
      if ($(window).width() < "768"){//mobile
        $( "html" ).has(".plone-toolbar-left").css({'margin-left':'0','margin-top':'0','margin-right':'0'});
        $( "html" ).has(".plone-toolbar-top").css({'margin-left':'0','margin-top':'0','margin-right':'0'});
        $( "html" ).has(".plone-toolbar-left.expanded").css({'margin-left':'0','margin-top':'0','margin-right':'0'});
        $( "#edit-zone" ).css("right", "-120px");
        $( "#edit-zone .plone-toolbar-logo" ).click(function() {
          if ($(this).hasClass("open")){
            $( "#edit-zone" ).css("right", "-120px");
            $( "html" ).css("margin-left", "0");
            $( "html" ).css("margin-right", "0");
            $(this).removeClass("open");
            $( "#edit-zone nav li" ).removeClass("active");
          } else {
            $( "#edit-zone" ).css("right", "0");
            $(this).addClass("open");
            $( "html" ).css("margin-left", "-120px");
            $( "html" ).css("margin-right", "120px");
          }
        });
        $( "#edit-zone nav li" ).has( "a .plone-toolbar-caret" ).click(function(e) {
          e.preventDefault();
          e.stopPropagation();
          if ($(this).hasClass("active")) {
            $( "#edit-zone" ).css("right", "0");
            $( "html" ).css("margin-left", "-120px");
            $( "html" ).css("margin-right", "120px");
            $( "#edit-zone nav li" ).removeClass("active");
          } else {
            $( "#edit-zone nav li" ).removeClass("active");
            $(this).addClass("active");
            $( "#edit-zone" ).css("right", "180px");
            $( "html" ).css("margin-left", "-300px");
            $( "html" ).css("margin-right", "300px");
          }
        });
      }
      else { //not mobile
        //left i top
        $( "html" ).has(".plone-toolbar-left").css({'margin-left':'60px','margin-top':'0','margin-right':'0'});
        $( "html" ).has(".plone-toolbar-top").css({'margin-left':'0','margin-top':'60px','margin-right':'0'});
        $( "html" ).has(".plone-toolbar-left.expanded").css({'margin-left':'120px','margin-top':'0','margin-right':'0'});
        if ($("#edit-zone").hasClass("plone-toolbar-left")) { //left
          $( "#edit-zone .plone-toolbar-logo" ).click(function() {
            if ($("#edit-zone").hasClass("expanded")){
              $( "#edit-zone" ).removeClass("expanded");
              $( "#edit-zone nav li" ).removeClass("active");
              $("html").css("margin-left", "120px");
            } else {
              $( "#edit-zone" ).addClass("expanded");
              $( "#edit-zone nav li" ).removeClass("active");
              $("html").css("margin-left", "60px");
            }
            $( "html" ).has(".plone-toolbar-left").css({'margin-left':'60px','margin-top':'0','margin-right':'0'});
            $( "html" ).has(".plone-toolbar-top").css({'margin-left':'0','margin-top':'60px','margin-right':'0'});
            $( "html" ).has(".plone-toolbar-left.expanded").css({'margin-left':'120px','margin-top':'0','margin-right':'0'});
          });
          $( "#edit-zone .plone-toolbar-logo" ).dblclick(function() {
            $("html").removeAttr("style");
            if ($("#edit-zone").hasClass("compressed")){
              $( "#edit-zone" ).removeClass("compressed");
            } else {
              $( "#edit-zone" ).addClass("compressed");
              $("html").css("margin-left", "0");
            }
          });
        } else { //top
          $( "#edit-zone .plone-toolbar-logo" ).click(function() {
            if ($("#edit-zone").hasClass("expanded")){
              $( "#edit-zone" ).removeClass("expanded");
              $( "#edit-zone nav li" ).removeClass("active");
              $("html").css("margin-top", "60px");
            } else {
              $( "#edit-zone" ).addClass("expanded");
              $( "#edit-zone nav li" ).removeClass("active");
              $("html").removeAttr("style");
              $("html").css("margin-top", "60px");
            }
            $( "html" ).has(".plone-toolbar-left").css({'margin-left':'60px','margin-top':'0','margin-right':'0'});
            $( "html" ).has(".plone-toolbar-top").css({'margin-left':'0','margin-top':'60px','margin-right':'0'});
            $( "html" ).has(".plone-toolbar-left.expanded").css({'margin-left':'120px','margin-top':'0','margin-right':'0'});
          });
          $( "#edit-zone .plone-toolbar-logo" ).dblclick(function() {
            $("html").removeAttr("style");
            if ($("#edit-zone").hasClass("compressed")){
              $( "#edit-zone" ).removeClass("compressed");
              $( "html" ).has(".plone-toolbar-top").css({'margin-left':'0','margin-top':'60px','margin-right':'0'});
            } else {
              $( "#edit-zone" ).addClass("compressed");
              $("html").removeAttr("padding-top", "0");
            }
          });
        }

        $( "#edit-zone nav > ul > li li" ).on('click', function(event) {
          event.stopImmediatePropagation();
        });

        //active
        $( "#edit-zone nav > ul > li" ).has( "a .plone-toolbar-caret" ).on('click', function(event) {
          event.preventDefault();
          event.stopPropagation();
          if ($(this).hasClass("active")) {
            $( "#edit-zone nav li" ).removeClass("active");
          } else {
            $("#edit-zone nav li").removeClass("active");
            $(this).addClass("active");
          }
        });

        //switcher -- provisional
        $( "#edit-zone .plone-toolbar-switcher" ).click(function() {
          if ($("#edit-zone").hasClass("plone-toolbar-top")) {
            $( "#edit-zone" ).addClass("plone-toolbar-left");
            $( "#edit-zone" ).removeClass("plone-toolbar-top");
          } else {
            $( "#edit-zone" ).addClass("plone-toolbar-top");
            $( "#edit-zone" ).removeClass("plone-toolbar-left");
          }
          $( "html" ).has(".plone-toolbar-left").css({'margin-left':'60px','margin-top':'0','margin-right':'0'});
          $( "html" ).has(".plone-toolbar-top").css({'margin-left':'0','margin-top':'60px','margin-right':'0'});
          $( "html" ).has(".plone-toolbar-left.expanded").css({'margin-left':'120px','margin-top':'0','margin-right':'0'});
        });
      }
    }
  });

  return Toolbar;
});
