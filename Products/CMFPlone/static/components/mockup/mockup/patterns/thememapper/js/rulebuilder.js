define([
  'jquery',
  'underscore',
  'backbone',
], function($, _, Backbone) {
  'use strict';

  var RuleBuilder = function(thememapper){
    /**
      * Rule builder
      *
      * Contains functions to build CSS and XPath selectors as well as a Diazo rule
      * from a given node, and acts as a state machine for the rules wizard.
      *
      */

    var self = this;
    self.thememapper = thememapper;

    self.themeInspector = null;
    self.unthemedInspector = null;

    self.active = false;
    self.currentScope = null;
    self.haveScrolled = false;

    self.ruleType = null;
    self.subtype = null;

    self._contentElement = null;
    self._themeElement = null;

    self.rulesFilename = 'rules.xml';

    self.ruleBuilderPopover = {
      el: self.thememapper.rulebuilderView.el,
      button: self.thememapper.rulebuilderView.triggerView.el,
      isOpened: function() {
        return $(this.el).is(":visible");
      },
      close: function() {
        if( this.isOpened() ) {
          if( self.active && $els.step2.is(":visible") )
          {
            self.end();
          }
          else
          {
            $(this.button).click();
          }
        }
      },
      load: function() {
        if( !this.isOpened() ) {
          $(this.button).click();
        }
      }
    };

    var $els = {
      reusePanel: $('#new-rule-reuse-panel'),
      reuseSelectors: $("#new-rule-reuse-selectors"),
      selectTheme: $("#new-rule-select-theme"),
      selectThemeNext: $("#new-rule-select-theme .next"),
      selectContentNext: $("#new-rule-select-content .next"),
      wizardSteps: $(".rule-wizard-step"),
      selectContent: $("#new-rule-select-content"),
      step1: $("#new-rule-step-1"),
      step1Next: $("#new-rule-step-1 .next"),
      step2: $("#new-rule-step-2"),
      step2Insert: $("#new-rule-step-2 .insert"),
      step2Copy: $("#new-rule-step-2 .copy"),
      inspectors: self.thememapper.$inspectorContainer,
      ruleOutput: $('#new-rule-output'),
      themePanel: $('#inspectors .mockup-inspector'),
      themePanelTop: $('.mockup-inspector .panel-toolbar'),
      unthemedPanel: $('#inspectors .unthemed-inspector'),
      unthemedPanelTop: $('.unthemed-inspector .panel-toolbar'),
      newRuleThemeChildren: $('#new-rule-theme-children'),
      newRuleUnthemedChildren: $('#new-rule-content-children'),
      modifiers: $('.rule-modifier'),
      selectors: $('.selector-info'),
      closers: $('.new-rule .close, .new-rule .wizard-cancel')
    };

    $els.step1Next.click(function() {
      var ruleType = self.getSelectedType();
      self.start(ruleType);
    });

    $els.closers.click(function() {
      self.end();
      self.ruleBuilderPopover.close();
    });

    $els.selectThemeNext.click(function() {
      self.themeInspector.on();

      if(!$els.inspectors.is(":visible")) {
        self.thememapper.showInspectors();
      }

      self.scrollTo($els.themePanelTop);
      self.ruleBuilderPopover.close();

      $els.themePanel.expose({
        color: "#fff",
        closeOnClick: false,
        closeOnEsc: false,
        closeSpeed: 0,
        onLoad: function() {
          self.scrollTo(this.getExposed());
        },
      });
    });

    $els.step2Copy.hide();
    $els.step2Insert.click(function() {

      var rule = $els.ruleOutput.val();

      var aceEditor = self.thememapper.fileManager.ace.editor;
      var session = aceEditor.getSession();

      function findStartTag(backwards) {
        aceEditor.find('<\\w+', {
          backwards: backwards,
          wrap: false,
          wholeWord: false,
          regExp: true
        });
      }

      function indent(string, amount) {
        var padding = '';
        for(var i = 0; i < amount; ++i) {
          padding += ' ';
        }
        return '\n' + padding + string.replace(/\n/g, '\n' + padding) + '\n';
      }

      //If we're already starting at the very end, go back to the beginning
      if( session.getDocument().$lines.length == aceEditor.getSelectionRange().end.row + 1)
      {
        aceEditor.navigateFileStart();
      }

      // Go to the next opening tag - we want to insert before this
      findStartTag(false);
      if(aceEditor.getCursorPosition().row <= 1) {
        // Probably the opening rules tag
        findStartTag(false);
      }

      var selectionText = aceEditor.getSelectedText();

      // If we didn't find anything, look for the end of the current tag
      if(selectionText == "") {
        aceEditor.find("(/>|</)", {
          backwards: false,
          wrap: false,
          wholeWord: false,
          regExp: true
        });

        var selectionText = aceEditor.getSelectedText();
        if(selectionText == "") {
          // Still nothing? Go to the end
          aceEditor.navigateFileEnd();
        } else {
          // Go one past the end tag, but first figure out how far we should i
          aceEditor.navigateDown();
        }
      }

      var indentation = aceEditor.getSelectionRange().start.column;
      var cursorPosition = aceEditor.getCursorPosition();
      var newlines = rule.match(/\n/g);
      var rows = 0;
      if(newlines != null) {
        rows = newlines.length;
      }

      aceEditor.gotoLine(cursorPosition.row);
      aceEditor.insert(indent(rule, indentation));
      aceEditor.getSelection().selectTo(cursorPosition.row + rows + 1, 0);
      aceEditor.gotoLine(cursorPosition.row);
      aceEditor.container.focus();

      self.ruleBuilderPopover.close();

      self.scrollTo(self.thememapper.fileManager.$el);

      // Clear the selection now that we're done with it
      self.unthemedInspector.save(null);
      self.themeInspector.save(null);
    });

    $els.selectContentNext.click(function() {
      self.unthemedInspector.on();
      if(!$els.inspectors.is(":visible")) {
        self.thememapper.showInspectors();
      }

      self.scrollTo($els.unthemedPanelTop);
      self.ruleBuilderPopover.close();

      $els.unthemedPanel.expose({
        color: "#fff",
        closeOnClick: false,
        closeOnEsc: false,
        closeSpeed: 0,
        onLoad: function() {
          self.scrollTo(this.getExposed());
        },
      });
    });

    $els.modifiers.change(function() {
      self.updateRule();
    });
    self.end = function() {
      self._contentElement = null;
      self._themeElement = null;
      self.currentScope = null;
      self.active = false;
      self.ruleType = null;
      self.subtype = null;

      self.callback(this);
    };

    self.start = function(ruleType) {
      var self = this;

      if( ruleType === undefined )
      {
        ruleType = self.getSelectedType();
      }

      self.themeInspector = self.thememapper.mockupInspector;
      self.unthemedInspector = self.thememapper.unthemedInspector;

      self._contentElement = null;
      self._themeElement = null;
      self.currentScope = "theme";

      // Drop rules get e.g. drop:content or drop:theme,
      // which predetermines the scope
      var ruleSplit = ruleType.split(':');
      if(ruleSplit.length >= 2) {
          self.ruleType = ruleSplit[0];
          self.subtype = ruleSplit[1];
          self.currentScope = self.subtype;
      } else{
          self.ruleType = ruleType;
          self.subtype = null;
      }

      self.active = true;

      self.callback(self);
    };

    /**
    * Build a diazo rule. 'themeChildren' and 'contentChildren' should be true or
    * false to indicate whether a -children selector is to be used.
    */
    self.buildRule = function(themeChildren, contentChildren) {
      if (self.ruleType === null) {
        return '';
      }

      if (self.subtype !== null) {
        if (self.subtype === 'content') {
          return '<' + self.ruleType + '\n    ' +
            self.calculateDiazoSelector(self._contentElement, 'content', contentChildren) +
            '\n    />';
        } else if (self.subtype === 'theme') {
          return '<' + self.ruleType + '\n    ' +
            self.calculateDiazoSelector(self._themeElement, 'theme', themeChildren) +
            '\n    />';
        }

      } else {
        return '<' + self.ruleType + '\n    ' +
          self.calculateDiazoSelector(self._themeElement, 'theme', themeChildren) + '\n    ' +
          self.calculateDiazoSelector(self._contentElement, 'content', contentChildren) +
          '\n    />';
      }

      // Should never happen
      return 'Error';
    };

    /**
    * Return a valid (but not necessarily unique) CSS selector for the given
    * element.
    */
    self.calculateCSSSelector = function(element) {
      var selector = element.tagName.toLowerCase();

      if (element.id) {
        selector += '#' + element.id;
      } else {
        var classes = $(element).attr('class');
        if(classes !== undefined) {
          var splitClasses = classes.split(/\s+/);
          for(var i = 0; i < splitClasses.length; i=i+1) {
            if(splitClasses[i] !== '' && splitClasses[i].indexOf('_theming') === -1) {
              selector += '.' + splitClasses[i];
              break;
            }
          }
        }
      }

      return selector;
    };

    /**
    * Return a valid, unqiue CSS selector for the given element. Returns null if
    * no reasoanble unique selector can be built.
    */
    self.calculateUniqueCSSSelector = function(element) {
      var paths = [];
      var path = null;

      var parents = $(element).parents();
      var ultimateParent = parents[parents.length - 1];

      while (element && element.nodeType === 1) {
        var selector = this.calculateCSSSelector(element);
            paths.splice(0, 0, selector);
            path = paths.join(' ');

        // The ultimateParent constraint is necessary since
        // this may be inside an iframe
        if($(path, ultimateParent).length === 1) {
          return path;
        }

        element = element.parentNode;
      }

      return null;
    };

    /**
    * Return a valid, unique XPath selector for the given element.
    */
    self.calculateUniqueXPathExpression = function(element) {
      var parents = $(element).parents();

      function elementIndex(e) {
        var siblings = $(e).siblings(e.tagName.toLowerCase());
        if(siblings.length > 0) {
          return '[' + ($(e).index() + 1) + ']';
        } else {
          return '';
        }
      }

      var xpathString = '/' + element.tagName.toLowerCase();
      if(element.id) {
        return '/' + xpathString + '[@id=\'' + element.id + '\']';
      } else {
        xpathString += elementIndex(element);
      }

      for(var i = 0; i < parents.length; i=i+1) {
        var p = parents[i];
        var pString = '/' + p.tagName.toLowerCase();

        if(p.id) {
          return '/' + pString + '[@id=\'' + p.id + '\']' + xpathString;
        } else {
          xpathString = pString + elementIndex(p) + xpathString;
        }
      }

      return xpathString;
    };

    /**
    * Return a unique CSS or XPath selector, preferring a CSS one.
    */
    self.bestSelector = function(element) {
      return self.calculateUniqueCSSSelector(element) ||
             self.calculateUniqueXPathExpression(element);
    };

    self.openRuleFile = function() {

      var fileManager = self.thememapper.fileManager;

      var treeNodes = fileManager.$tree.tree('getTree')
      var opened = false

      _.each(treeNodes.children, function(node) {
        if( node.name == self.rulesFilename )
        {
          //if it's open already, don't reopen it.
          //That will move the cursors location
          if( fileManager.$tabs.find('.active').data('path') != '/' + self.rulesFilename ) {
            self.thememapper.fileManager.openFile({node: node});
          }
          opened = true;
        }
      });
      return opened;
    };

    /**
    * Build a Diazo selector element with the appropriate namespace.
    */
    self.calculateDiazoSelector = function(element, scope, children) {
      var selectorType = scope;
      if(children) {
        selectorType += '-children';
      }

      var cssSelector = self.calculateUniqueCSSSelector(element);
      if(cssSelector) {
        return 'css:' + selectorType + '="' + cssSelector + '"';
      } else {
        var xpathSelector = self.calculateUniqueXPathExpression(element);
        return selectorType + '="' + xpathSelector + '"';
      }

    };

    self.select = function(element) {
      if(this.currentScope == "theme") {
        this._themeElement = element;
      } else if(this.currentScope == "content") {
        this._contentElement = element;
      }
    };

    self.getSelectedType = function() {
      var type = $("input[name='new-rule-type']:checked").val();
      return type;
    };

    self.next = function() {
        var self = this;
        if(self.subtype !== null) {
            // Drop rules have only one scope
            self.currentScope = null;
        } else {
            // Other rules have content and theme
            if(self.currentScope == "theme") {
                self.currentScope = "content";
            } else if (self.currentScope == "content") {
                self.currentScope = null;
            }
        }
        this.callback(this);
    };

    self.updateRule = function() {
        $els.ruleOutput.val(
            self.buildRule(
                $els.newRuleThemeChildren.is(':checked'),
                $els.newRuleUnthemedChildren.is(':checked')
            )
        );
    };

    self.scrollTo = function(selector) {
      if( $(selector).length == 0 ) {
        return;
      }

      $('html,body').animate({scrollTop: $(selector).offset().top}, 600);
    };

    /**
    *   Called by the rulebuilderView. If there are selected
    *   elements in the inspectors, we want to give the user the
    *   option to use those.
    */
    self.checkSelectors = function() {
      var selected = false;
      $('.selector-info').each(function() {
        if( $(this).text() != "" ) {
          //Theres an item selected, so show the option to use it
          $els.reusePanel.show();
          selected = true;
        }
      });
      if( !selected ) {
        //if we opened the panel previously, close it now
        $els.reusePanel.hide();
      }
      return selected;
    };
    self.callback = function(ruleBuilder) {
      $els.wizardSteps.hide();

      var themeFrameHighlighter = this.thememapper.mockupInspector;
      var unthemedFrameHighlighter = this.thememapper.unthemedInspector;

      if($.mask.isLoaded(true) && !self.ruleBuilderPopover.isOpened()) {
        self.scrollTo(self.thememapper.fileManager.$el);
        $.mask.close();
      }

      if(ruleBuilder.currentScope == 'theme') {
        if(themeFrameHighlighter.saved != null && $els.reuseSelectors.is(":checked")) {
          self.ruleBuilderPopover.close();

          // Use saved rule
          ruleBuilder.select(themeFrameHighlighter.saved);
          ruleBuilder.next();
        } else {
          // Let the frame highlighter perform a selection
          $els.selectTheme.show();
          if(!self.ruleBuilderPopover.isOpened()) {
            self.ruleBuilderPopover.load();
          }
        }

      } else if(ruleBuilder.currentScope == 'content') {
        if(unthemedFrameHighlighter.saved != null && $els.reuseSelectors.is(":checked")) {
          self.ruleBuilderPopover.close();

          // Use saved rule
          ruleBuilder.select(unthemedFrameHighlighter.saved);
          ruleBuilder.next();
        } else {
          // Let the frame highlighter perform a selection
          $els.selectContent.show();
          if(!self.ruleBuilderPopover.isOpened()) {
            self.ruleBuilderPopover.load();
          }
        }

      } else if(ruleBuilder.ruleType != null && ruleBuilder.currentScope == null) {

        $els.wizardSteps.hide();
        $els.step2.show();
        self.updateRule(ruleBuilder);

        if( self.openRuleFile() ) {
          $els.step2Insert.show();
        } else {
          $els.step2Insert.hide();
        }

        if(!self.ruleBuilderPopover.isOpened()) {
          self.ruleBuilderPopover.load();
        }

      } else { // end

        if(self.ruleBuilderPopover.isOpened()) {
          self.ruleBuilderPopover.close();
        }

        $els.wizardSteps.hide();
        $els.step1.show();
      }
    }
  };

  return RuleBuilder;
});
